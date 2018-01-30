from __future__ import print_function

import json
import logging

from autobahn.twisted.websocket import (WebSocketClientFactory,
                                        WebSocketClientProtocol, connectWS)
from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.python import log

# Python 2/3 compatibility import list
try:
    from collections import UserDict
except ImportError:
    from UserDict import UserDict

LOGGER = logging.getLogger('roslibpy')


class Message(UserDict):
    """Message objects used for publishing and subscribing to/from topics.

    A message is fundamentally a dictionary and behaves as one."""

    def __init__(self, values=None):
        self.data = {}
        if values is not None:
            self.update(values)


class ServiceRequest(UserDict):
    """Request for a service call."""

    def __init__(self, values=None):
        self.data = {}
        if values is not None:
            self.update(values)


class ServiceResponse(UserDict):
    """Response returned from a service call."""

    def __init__(self, values=None):
        self.data = {}
        if values is not None:
            self.update(values)


class Topic(object):
    """Publish and/or subscribe to a topic in ROS.

    Args:
        ros (:class:`.Ros`): Instance of the ROS connection.
        name (:obj:`str`): Topic name, e.g. ``/cmd_vel``.
        message_type (:obj:`str`): Message type, e.g. ``std_msgs/String``.
        throttle_rate (:obj:`int`): Rate (in ms between messages) at which to throttle the topics.
        queue_size (:obj:`int`): Queue size created at bridge side for re-publishing webtopics.
        latch (:obj:`bool`): True to latch the topic when publishing, False otherwise.
        queue_length (:obj:`int`): Queue length at bridge side used when subscribing.
    """

    def __init__(self, ros, name, message_type, latch=False, throttle_rate=0,
                 queue_size=100, queue_length=0):
        self.ros = ros
        self.name = name
        self.message_type = message_type
        self.latch = latch
        self.throttle_rate = throttle_rate
        self.queue_size = queue_size
        self.queue_length = queue_length

        self._subscribe_id = None
        self._advertise_id = None

        # TODO: Implement the following options
        # self.compression = options.compression || 'none';
        # self.reconnect_on_close = options.reconnect_on_close || true;
        self.compression = 'none'

    @property
    def is_advertised(self):
        """Indicate if the topic if current adversited or not.

        Returns:
            bool: True if advertised as publisher of this topic, False otherwise.
        """
        return self._advertise_id != None

    def subscribe(self, callback):
        """Register a subscription to the topic.

        Every time a message is published for the given topic,
        the callback will be called with the message object.

        Args:
            callback: Function to be called when messages of this topic are published.
        """
        # Avoid duplicate subscription
        if self._subscribe_id:
            return

        self._subscribe_id = 'subscribe:%s:%d' % (
            self.name, self.ros.id_counter)

        self.ros.on(self.name, callback)
        self.ros.send_on_ready(Message({
            'op': 'subscribe',
            'id': self._subscribe_id,
            'type': self.message_type,
            'topic': self.name,
            'compression': self.compression,
            'throttle_rate': self.throttle_rate,
            'queue_length': self.queue_length
        }))

    def unsubscribe(self, callback):
        """Unregister from a subscribed the topic.

        Args:
            callback: Function to unregister.
        """
        if not self._subscribe_id:
            return

        self.ros.off(self.name, callback)
        self.ros.send_on_ready(Message({
            'op': 'unsubscribe',
            'id': self._subscribe_id,
            'topic': self.name
        }))
        self._subscribe_id = None

    def publish(self, message):
        """Publish a message to the topic.

        Args:
            message (:class:`.Message`): ROS Brige Message to publish.
        """
        if not self.is_advertised:
            self.advertise()

        self.ros.send_on_ready(Message({
            'op': 'publish',
            'id': 'publish:%s:%d' % (self.name, self.ros.id_counter),
            'topic': self.name,
            'msg': dict(message),
            'latch': self.latch
        }))

    def advertise(self):
        """Register as a publisher for the topic."""
        if self.is_advertised:
            return

        self._advertise_id = 'advertise:%s:%d' % (
            self.name, self.ros.id_counter)

        self.ros.send_on_ready(Message({
            'op': 'advertise',
            'id': self._advertise_id,
            'type': self.message_type,
            'topic': self.name,
            'latch': self.latch,
            'queue_size': self.queue_size
        }))

        # TODO: Set _advertise_id=None on disconnect (if not reconnecting)

    def unadvertise(self):
        """Unregister as a publisher for the topic."""
        if not self.is_advertised:
            return

        self.ros.send_on_ready(Message({
            'op': 'unadvertise',
            'id': self._advertise_id,
            'topic': self.name,
        }))

        self._advertise_id = None


class RosBridgeProtocol(WebSocketClientProtocol):
    """Implements the websocket client protocol to encode/decode JSON ROS Brige messages."""

    def __init__(self, *args, **kwargs):
        super(RosBridgeProtocol, self).__init__(*args, **kwargs)
        self.factory = None
        self._pending_service_requests = {}
        self._message_handlers = {
            'publish': self._handle_publish,
            'service_response': self._handle_service_response
        }
        # TODO: add handlers for op: call_service, status

    def send_ros_message(self, message):
        """Encode and serialize ROS Brige protocol message.

        Args:
            message (:class:`.Message`): ROS Brige Message to send.
        """
        self.sendMessage(json.dumps(dict(message)).encode('utf8'))

    def register_message_handlers(self, op, handler):
        """Register a message handler for a specific operation type.

        Args:
            op (:obj:`str`): ROS Bridge operation.
            handler: Callback to handle the message.
        """
        if op in self._message_handlers:
            raise StandardError('Only one handler can be registered per operation')

        self._message_handlers[op] = handler

    def send_ros_service_request(self, service_request, callback, errback):
        """Initiate a ROS service request through the ROS Bridge.

        Args:
            service_request (:class:`.ServiceRequest`): Service request.
            callback: Callback invoked on successful execution.
            errback: Callback invoked on error.
        """
        request_id = service_request['id']
        self._pending_service_requests[request_id] = (callback, errback)

        self.sendMessage(json.dumps(dict(service_request)).encode('utf8'))

    def onConnect(self, response):
        LOGGER.debug('Server connected: %s', response.peer)

    def onOpen(self):
        LOGGER.debug('Connection to ROS MASTER ready.')
        self.factory.ready(self)

    def onMessage(self, payload, isBinary):
        if isBinary:
            raise NotImplementedError('Add support for binary messages')

        message = Message(json.loads(payload.decode('utf8')))
        handler = self._message_handlers.get(message['op'], None)
        if not handler:
            raise StandardError('No handler registered for operation "%s"' % message['op'])

        handler(message)

    def _handle_publish(self, message):
        self.factory.emit(message['topic'], message['msg'])

    def _handle_service_response(self, message):
        request_id = message['id']
        service_handlers = self._pending_service_requests.get(request_id, None)

        if not service_handlers:
            raise StandardError('No handler registered for service request ID: "%s"' % request_id)

        callback, errback = service_handlers
        del self._pending_service_requests[request_id]

        if 'result' in message and message['result'] == False:
            if errback:
                errback(message['values'])
        else:
            if callback:
                callback(ServiceRequest(message['values']))

    def onClose(self, wasClean, code, reason):
        LOGGER.info('WebSocket connection closed: %s', reason)


class RosBridgeClientFactory(ReconnectingClientFactory, WebSocketClientFactory):
    protocol = RosBridgeProtocol

    def __init__(self, *args, **kwargs):
        super(RosBridgeClientFactory, self).__init__(*args, **kwargs)
        self._on_ready_event = Deferred()
        self._event_subscribers = {}

    def on_ready(self, callback):
        self._on_ready_event.addCallback(callback)

    def ready(self, proto):
        self._on_ready_event.callback(proto)

    def on(self, event_name, callback):
        """Add a callback to an arbitrary named event."""
        if event_name not in self._event_subscribers:
            self._event_subscribers[event_name] = []

        subscribers = self._event_subscribers[event_name]
        if callback not in subscribers:
            subscribers.append(callback)

    def off(self, event_name, callback):
        """Remove a callback from an arbitrary named event."""
        if event_name not in self._event_subscribers:
            return

        subscribers = self._event_subscribers[event_name]
        if callback in subscribers:
            subscribers.remove(callback)

    def emit(self, event_name, *args):
        """Trigger a named event."""
        if event_name not in self._event_subscribers:
            return

        subscribers = self._event_subscribers[event_name]
        for subscriber in subscribers:
            subscriber(*args)

    def startedConnecting(self, connector):
        LOGGER.debug('Started to connect...')

    def clientConnectionLost(self, connector, reason):
        LOGGER.debug('Lost connection. Reason: %s', reason)
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        LOGGER.debug('Connection failed. Reason: %s', reason)
        ReconnectingClientFactory.clientConnectionFailed(
            self, connector, reason)
        self._on_ready_event.errback(reason)


class Ros(object):
    """Connection manager to ROS server."""

    def __init__(self, host, port):
        scheme = 'ws'
        self._id_counter = 0
        self.connector = None
        self.factory = RosBridgeClientFactory(
            u"%s://%s:%s" % (scheme, host, port))
        self._log_observer = log.PythonLoggingObserver()
        self._log_observer.start()

        self.connect()

    @property
    def id_counter(self):
        """Generate an auto-incremental ID starting from 1.

        Returns:
            int: An auto-incremented ID.
        """
        self._id_counter += 1
        return self._id_counter

    @property
    def is_connected(self):
        """Indicate if the ROS connection is open or not.

        Returns:
            bool: True if connected to ROS, False otherwise.
        """
        return self.connector and self.connector.state == 'connected'

    def connect(self):
        """Connect to ROS master."""
        # Don't try to reconnect if already connected.
        if self.is_connected:
            return

        self.connector = connectWS(self.factory)

    def close(self):
        """Disconnect from ROS master."""
        if self.connector:
            self.connector.disconnect()

    def run_event_loop(self):
        """Kick-starts the main event loop of the ROS client.

        The current implementation relies on Twisted Reactors
        to control the event loop."""
        reactor.run()

    def terminate(self):
        """Signals the termination of the main event loop."""
        reactor.stop()
        self._log_observer.stop()

    def on(self, event_name, callback):
        """Add a callback to an arbitrary named event."""
        self.factory.on(event_name, callback)

    def off(self, event_name, callback):
        """Remove a callback from an arbitrary named event."""
        self.factory.off(event_name, callback)

    def emit(self, event_name, *args):
        """Trigger a named event."""
        self.factory.emit(event_name, *args)

    def on_ready(self, callback, run_in_thread=False):
        """Add a callback to be executed when the connection is established.

        If a connection to ROS is already available, the callback is executed immediately.

        Args:
            callback: Callable function to be invoked when ROS connection is ready.
            run_in_thread (:obj:`bool`): True to run the callback in a separate thread, False otherwise.
        """
        def wrapper_callback(proto):
            if run_in_thread:
                reactor.callInThread(callback)
            else:
                callback()

            return proto

        self.factory.on_ready(wrapper_callback)

    def send_on_ready(self, message):
        """Send message to the ROS Master once the connection is established.

        If a connection to ROS is already available, the message is sent immediately.

        Args:
            message (:class:`.Message`): ROS Brige Message to send.
        """
        def send_internal(proto):
            proto.send_ros_message(message)
            return proto

        self.factory.on_ready(send_internal)

    def send_service_request(self, message, callback, errback):
        def send_internal(proto):
            proto.send_ros_service_request(message, callback, errback)
            return proto

        self.factory.on_ready(send_internal)
        
    def set_status_level(self, level, identifier):
        level_message = Message({
            'op': 'set_level',
            'level': level,
            'id': identifier
        })

        self.send_on_ready(level_message)


if __name__ == '__main__':

    import time

    FORMAT = '%(asctime)-15s [%(levelname)s] %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)

    ros_client = Ros('127.0.0.1', 9090)

    def run_subscriber_example():
        listener = Topic(ros_client, '/chatter', 'std_msgs/String')
        listener.subscribe(lambda message: LOGGER.info('Received message on: %s', message['data']))

    def run_publisher_example():
        publisher = Topic(ros_client, '/chatter', 'std_msgs/String')

        def start_sending():
            while ros_client.is_connected:
                message = Message({'data': 'test'})
                LOGGER.info('Publishing message to /chatter. %s', message)
                publisher.publish(message)

                time.sleep(0.75)
    
        ros_client.on_ready(start_sending, run_in_thread=True)

    run_publisher_example()

    try:
        ros_client.run_event_loop()
    except KeyboardInterrupt:
        ros_client.terminate()

    LOGGER.info('Stopped.')
