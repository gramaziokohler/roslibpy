from __future__ import print_function

import json

from . import Message, ServiceRequest


class Service(object):
    """Client to call ROS services.

    Args:
        ros (:class:`.Ros`): Instance of the ROS connection.
        name (:obj:`str`): Service name, e.g. ``/add_two_ints``.
        service_type (:obj:`str`): Service type, e.g. ``rospy_tutorials/AddTwoInts``.
    """

    def __init__(self, ros, name, service_type):
        self.ros = ros
        self.name = name
        self.service_type = service_type

        # self._service_callback = None
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
        """Creates a service call.

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

        client.call(request, lambda(result): callback(json.loads(result['value'])), errback)

    def set(self, value, callback=None, errback=None):
        """Set a new value to the parameter.

        Args:
            value: Value to set the parameter to.
            callback: Callable function to be invoked when the operation is completed.
            errback: Callback invoked on error.
        """
        client = Service(self.ros, '/rosapi/set_param', 'rosapi/SetParam')
        request = ServiceRequest({'name': self.name, 'value': json.dumps(value)})

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
    import logging
    from roslibpy import Ros

    FORMAT = '%(asctime)-15s [%(levelname)s] %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)

    ros_client = Ros('127.0.0.1', 9090)

    def run_get_example():
        param = Param(ros_client, 'run_id')
        param.get(print)

    def run_set_example():
        param = Param(ros_client, 'test_param')
        param.set('test_value')

    def run_delete_example():
        param = Param(ros_client, 'test_param')
        param.delete()

    run_delete_example()

    try:
        ros_client.run_event_loop()
    except KeyboardInterrupt:
        ros_client.terminate()


