from __future__ import print_function

from . import Message

# Python 2/3 compatibility import list
try:
    from collections import UserDict
except ImportError:
    from UserDict import UserDict


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
