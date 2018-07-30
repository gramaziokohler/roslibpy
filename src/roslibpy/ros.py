from __future__ import print_function

import logging

from . import Message, Service, ServiceRequest
from .comm import RosBridgeClientFactory

LOGGER = logging.getLogger('roslibpy')


class Ros(object):
    """Connection manager to ROS server."""

    def __init__(self, host, port=None, is_secure=False):
        self._id_counter = 0
        url = RosBridgeClientFactory.create_url(host, port, is_secure)
        self.factory = RosBridgeClientFactory(url)
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
        return self.factory.is_connected

    def connect(self):
        """Connect to ROS master."""
        # Don't try to reconnect if already connected.
        if self.is_connected:
            return

        self.factory.connect()

    def close(self):
        """Disconnect from ROS master."""
        if self.is_connected:
            def _wrapper_callback(proto):
                proto.send_close()
                return proto

            self.factory.on_ready(_wrapper_callback)

    def run_forever(self):
        """Kick-starts a blocking loop to wait for events.

        Depending on the implementations, and the client applications,
        running this might be required or not.
        """
        self.factory.manager.run_forever()

    def run_event_loop(self):
        LOGGER.warn('Deprecation warning: use run_forever instead of run_event_loop ')
        self.run_forever()

    def call_later(self, delay, callback):
        """Call the given function after a certain period of time has passed.

        Args:
            delay (:obj:`int`): Number of seconds to wait before invoking the callback.
            callback (:obj:`callable`): Callable function to be invoked when ROS connection is ready.
        """
        self.factory.manager.call_later(delay, callback)

    def terminate(self):
        """Signals the termination of the main event loop."""
        if self.is_connected:
            self.close()

        self.factory.manager.terminate()

    def on(self, event_name, callback):
        """Add a callback to an arbitrary named event."""
        self.factory.on(event_name, callback)

    def off(self, event_name, callback):
        """Remove a callback from an arbitrary named event."""
        self.factory.off(event_name, callback)

    def emit(self, event_name, *args):
        """Trigger a named event."""
        self.factory.emit(event_name, *args)

    def on_ready(self, callback, run_in_thread=True):
        """Add a callback to be executed when the connection is established.

        If a connection to ROS is already available, the callback is executed immediately.

        Args:
            callback: Callable function to be invoked when ROS connection is ready.
            run_in_thread (:obj:`bool`): True to run the callback in a separate thread, False otherwise.
        """
        def _wrapper_callback(proto):
            if run_in_thread:
                self.factory.manager.call_in_thread(callback)
            else:
                callback()

            return proto

        self.factory.on_ready(_wrapper_callback)

    def send_on_ready(self, message):
        """Send message to the ROS Master once the connection is established.

        If a connection to ROS is already available, the message is sent immediately.

        Args:
            message (:class:`.Message`): ROS Bridge Message to send.
        """
        def _send_internal(proto):
            proto.send_ros_message(message)
            return proto

        self.factory.on_ready(_send_internal)

    def send_service_request(self, message, callback, errback):
        """Send a service request to the ROS Master once the connection is established.

        If a connection to ROS is already available, the request is sent immediately.

        Args:
            message (:class:`.Message`): ROS Bridge Message containing the request.
            callback: Callback invoked on successful execution.
            errback: Callback invoked on error.
        """
        def _send_internal(proto):
            proto.send_ros_service_request(message, callback, errback)
            return proto

        self.factory.on_ready(_send_internal)

    def set_status_level(self, level, identifier):
        level_message = Message({
            'op': 'set_level',
            'level': level,
            'id': identifier
        })

        self.send_on_ready(level_message)

    def get_action_servers(self, callback, errback=None):
        """Retrieve list of action servers in ROS."""
        service = Service(self, '/rosapi/action_servers',
                          'rosapi/GetActionServers')

        service.call(ServiceRequest(), callback, errback)

    def get_topics(self, callback, errback=None):
        """Retrieve list of topics in ROS."""
        service = Service(self, '/rosapi/topics',
                          'rosapi/Topics')

        service.call(ServiceRequest(), callback, errback)

    def get_topics_for_type(self, topic_type, callback, errback=None):
        """Retrieve list of topics in ROS matching the specified type."""
        service = Service(self, '/rosapi/topics_for_type',
                          'rosapi/TopicsForType')

        service.call(ServiceRequest({'type': topic_type}), callback, errback)

    def get_services(self, callback, errback=None):
        """Retrieve list of active service names in ROS."""
        service = Service(self, '/rosapi/services',
                          'rosapi/Services')

        service.call(ServiceRequest(), callback, errback)

    def get_services_for_type(self, service_type, callback, errback=None):
        """Retrieve list of services in ROS matching the specified type."""
        service = Service(self, '/rosapi/services_for_type',
                          'rosapi/ServicesForType')

        service.call(ServiceRequest({'type': service_type}), callback, errback)

    def get_service_request_details(self, type, callback, errback=None):
        """Retrieve details of a ROS Service Request."""
        service = Service(self, '/rosapi/service_request_details',
                          'rosapi/ServiceRequestDetails')

        service.call(ServiceRequest({'type': type}), callback, errback)

    def get_service_response_details(self, type, callback, errback=None):
        """Retrieve details of a ROS Service Response."""
        service = Service(self, '/rosapi/service_response_details',
                          'rosapi/ServiceResponseDetails')

        service.call(ServiceRequest({'type': type}), callback, errback)

    def get_nodes(self, callback, errback=None):
        """Retrieve list of active node names in ROS."""
        service = Service(self, '/rosapi/nodes',
                          'rosapi/Nodes')

        service.call(ServiceRequest(), callback, errback)

    def get_node_details(self, node, callback, errback=None):
        """Retrieve list subscribed topics, publishing topics and services of a specific node name."""
        service = Service(self, '/rosapi/node_details',
                          'rosapi/NodeDetails')

        service.call(ServiceRequest({'node': node}), callback, errback)

    def get_params(self, callback, errback=None):
        """Retrieve list of param names from the ROS Parameter Server."""
        service = Service(self, '/rosapi/get_param_names',
                          'rosapi/GetParamNames')

        service.call(ServiceRequest(), callback, errback)

    def get_topic_type(self, topic, callback, errback=None):
        """Retrieve the type of a topic in ROS."""
        service = Service(self, '/rosapi/topic_type',
                          'rosapi/TopicType')

        service.call(ServiceRequest({'topic': topic}), callback, errback)

    def get_service_type(self, service_name, callback, errback=None):
        """Retrieve the type of a service in ROS."""
        service = Service(self, '/rosapi/service_type',
                          'rosapi/ServiceType')

        service.call(ServiceRequest(
            {'service': service_name}), callback, errback)

    def get_message_details(self, message_type, callback, errback=None):
        """Retrieve details of a message type in ROS."""
        service = Service(self, '/rosapi/message_details',
                          'rosapi/MessageDetails')

        service.call(ServiceRequest(
            {'type': message_type}), callback, errback)


if __name__ == '__main__':
    import logging

    FORMAT = '%(asctime)-15s [%(levelname)s] %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)

    ros_client = Ros('127.0.0.1', 9090)

    ros_client.on_ready(lambda: ros_client.get_topics(print))
    ros_client.call_later(3, ros_client.close)
    ros_client.call_later(5, ros_client.terminate)

    ros_client.run_forever()
