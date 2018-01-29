from __future__ import print_function

import json

from autobahn.twisted.websocket import (WebSocketClientFactory,
                                        WebSocketClientProtocol,
                                        connectWS)
from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.internet.protocol import ReconnectingClientFactory

# Python 2/3 compatibility import list
try:
    from collections import UserDict
except ImportError:
    from UserDict import UserDict


class Message(UserDict):
    """Message objects used for publishing and subscribing to/from topics.

    A message is fundamentally a dictionary and behaves as one."""
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
        self._is_advertised = False

        # TODO: Implement the following options
        # self.compression = options.compression || 'none';
        # self.reconnect_on_close = options.reconnect_on_close || true;
        self.compression = 'none'

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

    def publish(self, message):
        """Publish a message to the topic.

        Args:
            message (:class:`.Message`):  ROS Brige Message to publish.
        """
        if not self._is_advertised:
            self.advertise()

        self.ros.send_on_ready(Message({
            'op': 'publish',
            'id': 'publish:%s:%d' % (self.name, self.ros.id_counter-1),
            'topic': self.name,
            'msg': dict(message),
            'latch': self.latch
            }))

    def advertise(self):
        """Register as a publisher for the topic."""
        if self._is_advertised:
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

        self._is_advertised = True

        # TODO: Set _is_advertised=False on disconnect (if not reconnecting)


class RosBridgeProtocol(WebSocketClientProtocol):
    def send_ros_message(self, message):
        """Encode and serialize ROS Brige protocol message

        Args:
            message (:class:`.Message`): ROS Brige Message to send.
        """
        print('Sending', dict(message))
        self.sendMessage(json.dumps(dict(message)).encode('utf8'))

    def __init__(self, *args, **kwargs):
        super(RosBridgeProtocol, self).__init__(*args, **kwargs)
        self.factory = None

    def onConnect(self, response):
        print("Server connected: {0}".format(response.peer))

    def onOpen(self):
        self.factory.ready(self)

    def onMessage(self, payload, isBinary):
        if isBinary:
            raise NotImplementedError('Add support for binary messages')

        message = Message(json.loads(payload.decode('utf8')))

        if 'topic' in message:
            # TODO: Check if this is really the best way to emit
            # of if we should emit the full message variable
            self.factory.emit(message['topic'], message['msg'])

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))


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
        print('Started to connect.')

    def clientConnectionLost(self, connector, reason):
        print('Lost connection. Reason: {}'.format(reason))
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        print('Connection failed. Reason: {}'.format(reason))
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)
        self._on_ready_event.errback(reason)


class Ros(object):
    """Connection manager to ROS server."""
    def __init__(self, host, port):
        scheme = 'ws'
        self._id_counter = 0
        self.connector = None
        self.factory = RosBridgeClientFactory(u"%s://%s:%s" % (scheme, host, port))

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

    def on(self, event_name, callback):
        """Add a callback to an arbitrary named event."""
        self.factory.on(event_name, callback)

    def off(self, event_name, callback):
        """Remove a callback from an arbitrary named event."""
        self.factory.off(event_name, callback)

    def emit(self, event_name, *args):
        """Trigger a named event."""
        self.factory.emit(event_name, *args)

    def on_ready(self, callback):
        """Add a callback to be executed when the connection is established.

        If a connection to ROS is already available, the callback is executed immediately.
        """
        def wrapper_callback(proto):
            callback(proto)
            return proto

        self.factory.on_ready(wrapper_callback)

    def send_on_ready(self, message):
        """Send message to the ROS Master once the connection is established.

        If a connection to ROS is already available, the message is sent immediately.

        Args:
            message (:class:`.Message`): ROS Brige Message to send.
        """
        self.on_ready(lambda proto: proto.send_ros_message(message))

    def set_status_level(self, level, identifier):
        level_message = Message({
            'op': 'set_level',
            'level': level,
            'id': identifier
        })

        self.send_on_ready(level_message)


if __name__ == '__main__':

    import sys
    from twisted.python import log

    log.startLogging(sys.stdout)
    ros_client = Ros('127.0.0.1', 9090)

    listener = Topic(ros_client, '/chatter', 'std_msgs/String')
    # listener.publish(Message({'data': 'test'}))
    def gotMessage(message):
        print('Received message on: ' + message['data'])

    listener.subscribe(gotMessage)

    try:
        ros_client.run_event_loop()
    except KeyboardInterrupt:
        ros_client.terminate()

    print('Stopped.')
