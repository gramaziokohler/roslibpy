from __future__ import print_function

import logging
import threading

from autobahn.twisted.websocket import WebSocketClientFactory
from autobahn.twisted.websocket import WebSocketClientProtocol
from autobahn.twisted.websocket import connectWS
from autobahn.websocket.util import create_url
from twisted.internet import defer
from twisted.internet import reactor
from twisted.internet import threads
from twisted.internet.error import ConnectionDone
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.python import log

from ..event_emitter import EventEmitterMixin
from . import RosBridgeProtocol

LOGGER = logging.getLogger('roslibpy')


class AutobahnRosBridgeProtocol(RosBridgeProtocol, WebSocketClientProtocol):
    def __init__(self, *args, **kwargs):
        super(AutobahnRosBridgeProtocol, self).__init__(*args, **kwargs)

    def onConnect(self, response):
        LOGGER.debug('Server connected: %s', response.peer)

    def onOpen(self):
        LOGGER.info('Connection to ROS MASTER ready.')
        self.factory.ready(self)

    def onMessage(self, payload, isBinary):
        if isBinary:
            raise NotImplementedError('Add support for binary messages')

        try:
            self.on_message(payload)
        except Exception:
            LOGGER.exception('Exception on start_listening while trying to handle message received.' +
                             'It could indicate a bug in user code on message handlers. Message skipped.')

    def onClose(self, wasClean, code, reason):
        LOGGER.info('WebSocket connection closed: Code=%s, Reason=%s', str(code), reason)

    def send_message(self, payload):
        return self.sendMessage(payload, isBinary=False, fragmentSize=None, sync=False, doNotCompress=False)

    def send_close(self):
        self.sendClose()


class AutobahnRosBridgeClientFactory(EventEmitterMixin, ReconnectingClientFactory, WebSocketClientFactory):
    """Factory to create instances of the ROS Bridge protocol built on top of Autobahn/Twisted."""
    protocol = AutobahnRosBridgeProtocol

    def __init__(self, *args, **kwargs):
        super(AutobahnRosBridgeClientFactory, self).__init__(*args, **kwargs)
        self._proto = None
        self._manager = None
        self.connector = None
        self.setProtocolOptions(closeHandshakeTimeout=5)

    def connect(self):
        """Establish WebSocket connection to the ROS server defined for this factory."""
        self.connector = connectWS(self)

    @property
    def is_connected(self):
        """Indicate if the WebSocket connection is open or not.

        Returns:
            bool: True if WebSocket is connected, False otherwise.
        """
        return self.connector and self.connector.state == 'connected'

    def on_ready(self, callback):
        if self._proto:
            callback(self._proto)
        else:
            self.once('ready', callback)

    def ready(self, proto):
        self._proto = proto
        self.emit('ready', proto)

    def startedConnecting(self, connector):
        LOGGER.debug('Started to connect...')

    def clientConnectionLost(self, connector, reason):
        LOGGER.debug('Lost connection. Reason: %s', reason)
        self.emit('close', self._proto)

        # Do not try to reconnect if the connection was closed cleanl
        if reason.type is not ConnectionDone:
            ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

        self._proto = None

    def clientConnectionFailed(self, connector, reason):
        LOGGER.debug('Connection failed. Reason: %s', reason)
        ReconnectingClientFactory.clientConnectionFailed(
            self, connector, reason)
        self._proto = None

    @property
    def manager(self):
        """Get an instance of the event loop manager for this factory."""
        if not self._manager:
            self._manager = TwistedEventLoopManager()

        return self._manager

    @classmethod
    def create_url(cls, host, port=None, is_secure=False):
        url = host if port is None else create_url(host, port, is_secure)
        return url


class TwistedEventLoopManager(object):
    """Manage the main event loop using Twisted reactor.

    The event loop is a Twisted application is a very opinionated
    management strategy. Other communication layers use different
    event loop handlers that might be more fitting for different
    execution environments.
    """
    def __init__(self):
        self._log_observer = log.PythonLoggingObserver()
        self._log_observer.start()

    def run(self):
        """Kick-starts a non-blocking event loop.

        This implementation starts the Twisted Reactor
        on a separate thread to avoid blocking."""

        if reactor.running:
            LOGGER.warn('Twisted reactor is already running')
            return

        self._thread = threading.Thread(target=reactor.run, args=(False,))
        self._thread.daemon = True
        self._thread.start()

    def run_forever(self):
        """Kick-starts the main event loop of the ROS client.

        This implementation relies on Twisted Reactors
        to control the event loop."""
        reactor.run()

    def call_later(self, delay, callback):
        """Call the given function after a certain period of time has passed.

        Args:
            delay (:obj:`int`): Number of seconds to wait before invoking the callback.
            callback (:obj:`callable`): Callable function to be invoked when the delay has elapsed.
        """
        reactor.callLater(delay, callback)

    def call_in_thread(self, callback):
        """Call the given function on a thread.

        Args:
            callback (:obj:`callable`): Callable function to be invoked in a thread.
        """
        reactor.callInThread(callback)

    def blocking_call_from_thread(self, callback, timeout):
        """Call the given function from a thread, and wait for the result synchronously
        for as long as the timeout will allow.

        Args:
            callback: Callable function to be invoked from the thread.
            timeout (:obj: int): Number of seconds to wait for the response before
                raising an exception.

        Returns:
            The results from the callback, or a timeout exception.
        """
        result_placeholder = defer.Deferred()
        if timeout:
            result_placeholder.addTimeout(timeout, reactor, onTimeoutCancel=self.raise_timeout_exception)
        return threads.blockingCallFromThread(reactor, callback, result_placeholder)

    def raise_timeout_exception(self, _result=None, _timeout=None):
        """Callback called on timeout.

        Args:
            _result: Unused--required by Twister.
            _timeout: Unused--required by Twister.

        Raises:
            An exception.
        """
        raise Exception('No service response received')

    def get_inner_callback(self, result_placeholder):
        """Get the callback which, when called, provides result_placeholder with the result.

        Args:
            result_placeholder: (:obj: Deferred): Object in which to store the result.

        Returns:
            A callable which provides result_placeholder with the result in the case of success.
        """
        def inner_callback(result):
            result_placeholder.callback({'result': result})
        return inner_callback

    def get_inner_errback(self, result_placeholder):
        """Get the errback which, when called, provides result_placeholder with the error.

        Args:
            result_placeholder: (:obj: Deferred): Object in which to store the result.

        Returns:
            A callable which provides result_placeholder with the error in the case of failure.
        """
        def inner_errback(error):
            result_placeholder.callback({'exception': error})
        return inner_errback

    def terminate(self):
        """Signals the termination of the main event loop."""
        if reactor.running:
            reactor.stop()

        self._log_observer.stop()
