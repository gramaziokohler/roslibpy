from __future__ import print_function

import helpers

from roslibpy import Message, Ros, Topic


def run_topic_pubsub():
    context = {'counter': 0}
    ros_client = Ros('127.0.0.1', 9090)
    listener = Topic(ros_client, '/chatter', 'std_msgs/String')
    publisher = Topic(ros_client, '/chatter', 'std_msgs/String')

    def receive_message(message):
        context['counter'] += 1
        assert(message['data'] == 'test')

        if context['counter'] == 3:
            ros_client.terminate()

    def start_sending():
        message = Message({'data': 'test'})
        publisher.publish(message)
        publisher.publish(message)
        publisher.publish(message)
        publisher.unadvertise()

    def start_receiving():
        listener.subscribe(receive_message)

    ros_client.on_ready(start_receiving, run_in_thread=True)
    ros_client.on_ready(start_sending, run_in_thread=True)
    ros_client.run_event_loop()


def test_topic_pubsub():
    helpers.run_as_process(run_topic_pubsub)
