from __future__ import print_function

import logging

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


if __name__ == '__main__':

    import time
    from . import Ros
    from twisted.internet import reactor

    FORMAT = '%(asctime)-15s [%(levelname)s] %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)

    ros_client = Ros('127.0.0.1', 9090)

    def run_subscriber_example():
        listener = Topic(ros_client, '/chatter', 'std_msgs/String')
        listener.subscribe(lambda message: LOGGER.info('Received message on: %s', message['data']))

    def run_unsubscriber_example():
        listener = Topic(ros_client, '/chatter', 'std_msgs/String')

        def print_message(message):
            LOGGER.info('Received message on: %s', message['data'])

        listener.subscribe(print_message)

        reactor.callLater(5, lambda: listener.unsubscribe(print_message))
        reactor.callLater(10, lambda: listener.subscribe(print_message))

    def run_publisher_example():
        publisher = Topic(ros_client, '/chatter', 'std_msgs/String')

        def start_sending():
            i = 0
            while ros_client.is_connected and i < 5:
                i += 1
                message = Message({'data': 'test'})
                LOGGER.info('Publishing message to /chatter. %s', message)
                publisher.publish(message)

                time.sleep(0.75)

            publisher.unadvertise()

        ros_client.on_ready(start_sending, run_in_thread=True)

    def run_service_example():
        from . import Service
        def h1(x):
            print('ok', x)

        def h2(x):
            print('error', x)

        service = Service(ros_client, '/turtle1/teleport_relative',
                          'turtlesim/TeleportRelative')
        service.call(ServiceRequest({'linear': 2, 'angular': 2}), h1, h2)

    def run_turtle_subscriber_example():
        listener = Topic(ros_client, '/turtle1/pose',
                         'turtlesim/Pose', throttle_rate=500)

        def print_message(message):
            LOGGER.info('Received message on: %s', message)

        listener.subscribe(print_message)

    run_turtle_subscriber_example()

    try:
        ros_client.run_event_loop()
    except KeyboardInterrupt:
        ros_client.terminate()

    LOGGER.info('Stopped.')
