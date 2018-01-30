from __future__ import print_function

import logging

from autobahn.twisted.websocket import connectWS
from twisted.internet import reactor
from twisted.python import log

from . import Message
from .comm import RosBridgeClientFactory

LOGGER = logging.getLogger('roslibpy')


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
        def _wrapper_callback(proto):
            if run_in_thread:
                reactor.callInThread(callback)
            else:
                callback()

            return proto

        self.factory.on_ready(_wrapper_callback)

    def send_on_ready(self, message):
        """Send message to the ROS Master once the connection is established.

        If a connection to ROS is already available, the message is sent immediately.

        Args:
            message (:class:`.Message`): ROS Brige Message to send.
        """
        def _send_internal(proto):
            proto.send_ros_message(message)
            return proto

        self.factory.on_ready(_send_internal)

    def send_service_request(self, message, callback, errback):
        """Send a service request to the ROS Master once the connection is established.

        If a connection to ROS is already available, the request is sent immediately.

        Args:
            message (:class:`.Message`): ROS Brige Message containing the request.
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
