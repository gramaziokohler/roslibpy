from __future__ import print_function

import logging

from autobahn.twisted.websocket import WebSocketClientFactory, WebSocketClientProtocol, connectWS
from twisted.internet.protocol import ReconnectingClientFactory

from . import RosBridgeProtocol
from .. import Message, ServiceResponse
from ..event_emitter import EventEmitterMixin

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

        self.on_message(payload)

    def onClose(self, wasClean, code, reason):
        LOGGER.info('WebSocket connection closed: %s', reason)

    def send_message(self, payload):
        return self.sendMessage(payload, isBinary=False, fragmentSize=None, sync=False, doNotCompress=False)

    def send_close(self):
        self.sendClose()

class AutobahnRosBridgeClientFactory(EventEmitterMixin, ReconnectingClientFactory, WebSocketClientFactory):
    """Factory to construct instance of the ROS Bridge protocol."""
    protocol = AutobahnRosBridgeProtocol

    def __init__(self, *args, **kwargs):
        super(AutobahnRosBridgeClientFactory, self).__init__(*args, **kwargs)
        self._proto = None
        self.connector = None
        self.setProtocolOptions(closeHandshakeTimeout=5)

    def connect(self):
        """Establish WebSocket connection to the ROS server defined for this factory.

        Returns:
            connector: An object which implements `twisted.interface.IConnector <http://twistedmatrix.com/documents/current/api/twisted.internet.interfaces.IConnector.html>`_.
        """
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
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)
        self._proto = None

    def clientConnectionFailed(self, connector, reason):
        LOGGER.debug('Connection failed. Reason: %s', reason)
        ReconnectingClientFactory.clientConnectionFailed(
            self, connector, reason)
        self._proto = None
