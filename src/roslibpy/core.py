from __future__ import print_function

import json
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
        compression (:obj:`str`): Type of compression to use, e.g. `png`. Defaults to `None`.
        throttle_rate (:obj:`int`): Rate (in ms between messages) at which to throttle the topics.
        queue_size (:obj:`int`): Queue size created at bridge side for re-publishing webtopics.
        latch (:obj:`bool`): True to latch the topic when publishing, False otherwise.
        queue_length (:obj:`int`): Queue length at bridge side used when subscribing.
    """
    SUPPORTED_COMPRESSION_TYPES = ('png', 'none')

    def __init__(self, ros, name, message_type, compression=None, latch=False, throttle_rate=0,
                 queue_size=100, queue_length=0):
        self.ros = ros
        self.name = name
        self.message_type = message_type
        self.compression = compression
        self.latch = latch
        self.throttle_rate = throttle_rate
        self.queue_size = queue_size
        self.queue_length = queue_length

        self._subscribe_id = None
        self._advertise_id = None

        if self.compression is None:
            self.compression = 'none'

        if self.compression not in self.SUPPORTED_COMPRESSION_TYPES:
            raise ValueError(
                'Unsupported compression type. Must be one of: ' + str(self.SUPPORTED_COMPRESSION_TYPES))

        # TODO: Implement the following options
        # self.reconnect_on_close = options.reconnect_on_close || true;

    @property
    def is_advertised(self):
        """Indicate if the topic is currently advertised or not.

        Returns:
            bool: True if advertised as publisher of this topic, False otherwise.
        """
        return self._advertise_id is not None

    @property
    def is_subscribed(self):
        """Indicate if the topic is currently subscribed or not.

        Returns:
            bool: True if subscribed to this topic, False otherwise.
        """
        return self._subscribe_id is not None

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

    def unsubscribe(self):
        """Unregister from a subscribed the topic."""
        if not self._subscribe_id:
            return

        self.ros.off(self.name)
        self.ros.send_on_ready(Message({
            'op': 'unsubscribe',
            'id': self._subscribe_id,
            'topic': self.name
        }))
        self._subscribe_id = None

    def publish(self, message):
        """Publish a message to the topic.

        Args:
            message (:class:`.Message`): ROS Bridge Message to publish.
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


class Service(object):
    """Client/server of ROS services.

    This class can be used both to consume other ROS services as a client,
    or to provide ROS services as a server.

    Args:
        ros (:class:`.Ros`): Instance of the ROS connection.
        name (:obj:`str`): Service name, e.g. ``/add_two_ints``.
        service_type (:obj:`str`): Service type, e.g. ``rospy_tutorials/AddTwoInts``.
    """

    def __init__(self, ros, name, service_type):
        self.ros = ros
        self.name = name
        self.service_type = service_type

        self._service_callback = None
        self._is_advertised = False

    @property
    def is_advertised(self):
        """Service servers are registered as advertised on ROS.

        This class can be used to be a service client or a server.

        Returns:
            bool: True if this is a server, False otherwise.
        """
        return self._is_advertised

    def call(self, request, callback, errback):
        """Start a service call.

        The service response is returned in the callback. If the
        service is currently advertised, this call does nothing.

        Args:
            request (:class:`.ServiceRequest`): Service request.
            callback: Callback invoked on successful execution.
            errback: Callback invoked on error.
        """
        if self.is_advertised:
            return

        service_call_id = 'call_service:%s:%d' % (
            self.name, self.ros.id_counter)

        self.ros.send_service_request(Message({
            'op': 'call_service',
            'id': service_call_id,
            'service': self.name,
            'args': dict(request),
        }), callback, errback)

    def advertise(self, callback):
        """Start advertising the service.

        This turns the instance from a client into a server. The callback will be
        invoked with every request that is made to the service.

        Args:
            callback: Callback invoked on every service call. It should accept two parameters: `service_request` and
                `service_response`. It should return `True` if executed correctly, otherwise `False`.
        """
        if self.is_advertised:
            return

        if not callable(callback):
            raise ValueError('Callback is not a valid callable')

        self._service_callback = callback
        self.ros.on(self.name, self._service_response_handler)
        self.ros.send_on_ready(Message({
            'op': 'advertise_service',
            'type': self.service_type,
            'service': self.name
        }))
        self._is_advertised = True

    def unadvertise(self):
        """Unregister as a service server."""
        if not self.is_advertised:
            return

        self.ros.send_on_ready(Message({
            'op': 'unadvertise_service',
            'service': self.name,
        }))
        self.ros.off(self.name, self._service_response_handler)

        self._is_advertised = False

    def _service_response_handler(self, request):
        response = ServiceResponse()
        success = self._service_callback(request['args'], response)

        call = Message({'op': 'service_response',
                        'service': self.name,
                        'values': dict(response),
                        'result': success
                        })

        if 'id' in request:
            call['id'] = request['id']

        self.ros.send_on_ready(call)


class Param(object):
    """A ROS parameter.

    Args:
        ros (:class:`.Ros`): Instance of the ROS connection.
        name (:obj:`str`): Parameter name, e.g. ``max_vel_x``.
    """

    def __init__(self, ros, name):
        self.ros = ros
        self.name = name

    def get(self, callback=None, errback=None):
        """Fetch the current value of the parameter.

        Args:
            callback: Callable function to be invoked when the operation is completed.
            errback: Callback invoked on error.
        """
        client = Service(self.ros, '/rosapi/get_param', 'rosapi/GetParam')
        request = ServiceRequest({'name': self.name})

        client.call(request, lambda result: callback(
            json.loads(result['value'])), errback)

    def set(self, value, callback=None, errback=None):
        """Set a new value to the parameter.

        Args:
            value: Value to set the parameter to.
            callback: Callable function to be invoked when the operation is completed.
            errback: Callback invoked on error.
        """
        client = Service(self.ros, '/rosapi/set_param', 'rosapi/SetParam')
        request = ServiceRequest(
            {'name': self.name, 'value': json.dumps(value)})

        client.call(request, callback, errback)

    def delete(self, callback=None, errback=None):
        """Delete the parameter.

        Args:
            callback: Callable function to be invoked when the operation is completed.
            errback: Callback invoked on error.
        """
        client = Service(self.ros, '/rosapi/delete_param',
                         'rosapi/DeleteParam')
        request = ServiceRequest({'name': self.name})

        client.call(request, callback, errback)


if __name__ == '__main__':

    import time
    from . import Ros

    FORMAT = '%(asctime)-15s [%(levelname)s] %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)

    ros_client = Ros('127.0.0.1', 9090)

    def run_subscriber_example():
        listener = Topic(ros_client, '/chatter', 'std_msgs/String')
        listener.subscribe(lambda message: LOGGER.info(
            'Received message on: %s', message['data']))

    def run_unsubscriber_example():
        listener = Topic(ros_client, '/chatter', 'std_msgs/String')

        def print_message(message):
            LOGGER.info('Received message on: %s', message['data'])

        listener.subscribe(print_message)

        ros_client.call_later(5, lambda: listener.unsubscribe(print_message))
        ros_client.call_later(10, lambda: listener.subscribe(print_message))

    def run_publisher_example():
        publisher = Topic(ros_client, '/chatter',
                          'std_msgs/String', compression='png')

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

    def run_get_example():
        param = Param(ros_client, 'run_id')
        param.get(print)

    def run_set_example():
        param = Param(ros_client, 'test_param')
        param.set('test_value')

    def run_delete_example():
        param = Param(ros_client, 'test_param')
        param.delete()

    def run_server_example():
        service = Service(ros_client, '/test_server',
                          'rospy_tutorials/AddTwoInts')

        def dispose_server():
            service.unadvertise()
            ros_client.call_later(1, service.ros.terminate)

        def add_two_ints(request, response):
            response['sum'] = request['a'] + request['b']
            if response['sum'] == 42:
                ros_client.call_later(2, dispose_server)

            return True

        service.advertise(add_two_ints)

    run_server_example()
    ros_client.run_forever()
