from __future__ import print_function

import random
import time

from twisted.internet import reactor

from . import Message, Topic
from .core import EventEmitterMixin


class Goal(EventEmitterMixin):
    """Goal for an action server.

    Args:
        action_client (:class:`.ActionClient`): Instance of the action client associated with the goal.
        goal_message (:class:`.Message`): Goal for the action server.
    """
    def __init__(self, action_client, goal_message):
        super(Goal, self).__init__()

        self.action_client = action_client
        self.goal_message = goal_message
        self.goal_id = 'goal_%s_%d' % (random.random(), time.time() * 1000)

        self.result = None
        self.status = None
        self.feedback = None

        self.goal_message = Message({
            'goal_id': {
                'stamp': {
                    'secs': 0,
                    'nsecs': 0
                },
                'id': self.goal_id
            },
            'goal': dict(self.goal_message)
        })

        self.action_client.add_goal(self)

        self.on('status', self._set_status)
        self.on('result', self._set_result)
        self.on('feedback', self._set_feedback)

    def send(self, timeout=None):
        """Send goal to the action server.

        Args:
            timeout (:obj:`int`): Timeout for the goal's result expressed in milliseconds.
        """
        self.action_client.goal_topic.publish(self.goal_message)
        if timeout:
          reactor.callLater(timeout / 1000., self._trigger_timeout)

    def cancel(self):
        """Cancel the current goal."""
        self.action_client.cancel_topic.publish(Message({'id': self.goal_id}))

    def _trigger_timeout(self):
        if not self.is_finished:
            self.emit('timeout')

    def _set_status(self, status):
        self.status = status

    def _set_result(self, result):
        self.result = result

    def _set_feedback(self, feedback):
        self.feedback = feedback

    @property
    def is_finished(self):
        """Indicate if the goal is finished or not.

        Returns:
            bool: True if finished, False otherwise.
        """
        return self.result != None


class ActionClient(object):
    """Client to use ROS actions.

    Args:
        ros (:class:`.Ros`): Instance of the ROS connection.
        server_name (:obj:`str`): Action server name, e.g. ``/fibonacci``.
        action_name (:obj:`str`): Action message name, e.g. ``actionlib_tutorials/FibonacciAction``.
        timeout (:obj:`int`): Connection timeout.
    """
    def __init__(self, ros, server_name, action_name, timeout=None,
                 omit_feedback=False, omit_status=False, omit_result=False):
        self.ros = ros
        self.server_name = server_name
        self.action_name = action_name
        self.timeout = timeout
        self.omit_feedback = omit_feedback
        self.omit_status = omit_status
        self.omit_result = omit_result
        self.goals = {}

        self._received_status = False

        # Create the topics associated with actionlib
        self.feedback_listener = Topic(ros, server_name + '/feedback', action_name + 'Feedback')
        self.status_listener = Topic(ros, server_name + '/status', 'actionlib_msgs/GoalStatusArray')
        self.result_listener = Topic(ros, server_name + '/result', action_name + 'Result')
        self.goal_topic = Topic(ros, server_name + '/goal', action_name + 'Goal')
        self.cancel_topic = Topic(ros, server_name + '/cancel', 'actionlib_msgs/GoalID')

        # Advertise the goal and cancel topics
        self.goal_topic.advertise()
        self.cancel_topic.advertise()

        # Subscribe to the status topic
        if not self.omit_status:
            self.status_listener.subscribe(self._on_status_message)

        # Subscribe to the feedback topic
        if not self.omit_feedback:
            self.feedback_listener.subscribe(self._on_feedback_message)

        # Subscribe to the result topic
        if not self.omit_result:
            self.result_listener.subscribe(self._on_result_message)

        """
        // If timeout specified, emit a 'timeout' event if the action server does not respond
        if (this.timeout) {
            setTimeout(function() {
            if (!receivedStatus) {
                that.emit('timeout');
            }
            }, this.timeout);
        }
        }
        """


    def _on_status_message(self, message):
        self._received_status = True

        for status in message['status_list']:
            goal = self.goals[status['goal_id']['id']]
            if goal:
                goal.emit('status', status)

    def _on_feedback_message(self, message):
        goal_id = message['status']['goal_id']['id']

        goal = self.goals[goal_id]
        if goal:
            goal.emit('status', message['status'])
            goal.emit('feedback', message['feedback'])

    def _on_result_message(self, message):
        goal_id = message['status']['goal_id']['id']

        goal = self.goals[goal_id]
        if goal:
            goal.emit('status', message['status'])
            goal.emit('result', message['result'])

    def add_goal(self, goal):
        """Add a goal to this action client.

        Args:
            goal (:class:`.Goal`): Goal to add.
        """
        self.goals[goal.goal_id] = goal

    def cancel(self):
        """Cancel all goals associated with this action client."""
        self.cancel_topic.publish(Message())

    def dispose(self):
        """Unsubscribe and unadvertise all topics associated with this action client."""
        self.goal_topic.unadvertise()
        self.cancel_topic.unadvertise()

        if not self.omit_status:
            self.status_listener.unsubscribe(self._on_status_message)
        if not self.omit_feedback:
            self.feedback_listener.unsubscribe(self._on_feedback_message)
        if not self.omit_result:
            self.result_listener.unsubscribe(self._on_result_message)


if __name__ == '__main__':
    import time
    import logging
    from . import Ros
    from twisted.internet import reactor

    FORMAT = '%(asctime)-15s [%(levelname)s] %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)

    ros_client = Ros('127.0.0.1', 9090)

    def run_action_example():
        action_client = ActionClient(ros_client, '/follow_joint_trajectory',
                                     'control_msgs/FollowJointTrajectoryAction')

    run_action_example()

    try:
        ros_client.run_event_loop()
    except KeyboardInterrupt:
        ros_client.terminate()
