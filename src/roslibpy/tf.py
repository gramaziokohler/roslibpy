"""
TF
==

ROS provides a very powerful transform library called `TF2 <http://wiki.ros.org/tf2>`_,
which lets the user keep track of multiple coordinate frames over time.

The **roslibpy** library offers access to it through the
`tf2_web_republisher <http://wiki.ros.org/tf2_web_republisher>`_
via the :class:`TFClient` class.

.. autoclass:: TFClient
   :members:

"""
from __future__ import print_function

import logging
import math

from . import Service, ServiceRequest, Topic

LOGGER = logging.getLogger('roslibpy.tf')


class TFClient(object):
    """A TF Client that listens to TFs from tf2_web_republisher.

    Args:
        ros (:class:`.Ros`): Instance of the ROS connection.
        fixed_frame (:obj:`str`): Fixed frame, e.g. ``/base_link``.
        angular_threshold (:obj:`float`): Angular threshold for the TF republisher.
        translation_threshold (:obj:`float`): Translation threshold for the TF republisher.
        rate (:obj:`float`): Rate for the TF republisher.
        update_delay (:obj:`int`): Time expressed in milliseconds to wait after a new subscription to update the TF republisher's list of TFs.
        topic_timeout (:obj:`int`): Timeout parameter for the TF republisher expressed in milliseconds.
        repub_service_name (:obj:`str`): Name of the republish tfs service, e.g. ``/republish_tfs``.
    """

    def __init__(self, ros, fixed_frame='/base_link', angular_threshold=2.0, translation_threshold=0.01, rate=10.0, update_delay=50, topic_timeout=2000.0,
                 server_name='/tf2_web_republisher', repub_service_name='/republish_tfs'):
        self.ros = ros
        self.fixed_frame = fixed_frame
        self.angular_threshold = angular_threshold
        self.translation_threshold = translation_threshold
        self.rate = rate
        self.update_delay = update_delay

        seconds = topic_timeout / 1000.
        secs = math.floor(seconds)
        nsecs = math.floor((seconds - secs) * 1000000000)
        self.topic_timeout = dict(secs=secs, nsecs=nsecs)
        self.repub_service_name = repub_service_name

        self.current_topic = False
        self.frame_info = {}
        self.republisher_update_requested = False

        self.service_client = Service(ros, self.repub_service_name,
                                      'tf2_web_republisher/RepublishTFs')

    def _process_tf_array(self, tf):
        """Process an incoming TF message and send it out using the callback functions.

        Args:
            tf (:obj:`list`): TF message from the server.
        """
        # TODO: Test this function
        for transform in tf['transforms']:
            frame_id = self._normalize_frame_id(transform['child_frame_id'])
            frame = self.frame_info.get(frame_id, None)

            if frame:
                frame['transform'] = dict(
                    translation=transform['transform']['translation'],
                    rotation=transform['transform']['rotation']
                )
                for callback in frame['cbs']:
                    callback(frame['transform'])

    def update_goal(self):
        """Send a new service request to the tf2_web_republisher based on the current list of TFs."""
        message = dict(source_frames=list(self.frame_info.keys()),
                       target_frame=self.fixed_frame,
                       angular_thres=self.angular_threshold,
                       trans_thres=self.translation_threshold,
                       rate=self.rate)

        # In contrast to roslibjs, we do not support groovy compatibility mode
        # and only use the service interface to the TF republisher
        message['timeout'] = self.topic_timeout
        request = ServiceRequest(message)

        self.service_client.call(
            request, self._process_response, self._process_error)

        self.republisher_update_requested = False

    def _process_error(self, response):
        LOGGER.error('The TF republisher service interface returned an error. %s', str(response))

    def _process_response(self, response):
        """Process the service response and subscribe to the tf republisher topic."""
        LOGGER.info('Received response from TF Republisher service interface')

        if self.current_topic:
            self.current_topic.unsubscribe(self._process_tf_array)

        self.current_topic = Topic(
            self.ros, response['topic_name'], 'tf2_web_republisher/TFArray')
        self.current_topic.subscribe(self._process_tf_array)

    def _normalize_frame_id(self, frame_id):
        # Remove leading slash, if it's there
        if frame_id[0] == '/':
            return frame_id[1:]

        return frame_id

    def subscribe(self, frame_id, callback):
        """Subscribe to the given TF frame.

        Args:
            frame_id (:obj:`str`):  TF frame identifier to subscribe to.
            callback (:obj:`callable`): A callable functions receiving one parameter with `transform` data.
        """

        frame_id = self._normalize_frame_id(frame_id)
        frame = self.frame_info.get(frame_id, None)

        # If there is no callback registered for the given frame, create emtpy callback list
        if not frame:
            frame = dict(cbs=[])
            self.frame_info[frame_id] = frame

            if not self.republisher_update_requested:
                self.ros.call_later(self.update_delay / 1000., self.update_goal)
                self.republisher_update_requested = True
        else:
            # If we already have a transform, call back immediately
            if 'transform' in frame:
                callback(frame['transform'])

        frame['cbs'].append(callback)

    def unsubscribe(self, frame_id, callback):
        """Unsubscribe from the given TF frame.

        Args:
            frame_id (:obj:`str`):  TF frame identifier to unsubscribe from.
            callback (:obj:`callable`): The callback function to remove.
        """

        frame_id = self._normalize_frame_id(frame_id)
        frame = self.frame_info.get(frame_id, None)

        if 'cbs' in frame:
            frame['cbs'].pop(callback)

        if not callback or ('cbs' in frame and len(frame['cbs']) == 0):
            self.frame_info.pop(frame_id)

    def dispose(self):
        """Unsubscribe and unadvertise all topics associated with this instance."""
        if self.current_topic:
            self.current_topic.unsubscribe(self._process_tf_array)


if __name__ == '__main__':
    import logging
    from roslibpy import Ros

    FORMAT = '%(asctime)-15s [%(levelname)s] %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)

    ros_client = Ros('127.0.0.1', 9090)

    def run_tf_example():
        tfclient = TFClient(ros_client, fixed_frame='world',
                            angular_threshold=0.01, translation_threshold=0.01)

        tfclient.subscribe('turtle2', print)

        def dispose_server():
            tfclient.dispose()

        ros_client.call_later(10, dispose_server)
        ros_client.call_later(11, ros_client.close)
        ros_client.call_later(12, ros_client.terminate)

    run_tf_example()
    ros_client.run_forever()
