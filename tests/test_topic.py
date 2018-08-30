from __future__ import print_function

import time

import helpers

from roslibpy import Message, Ros, Topic


def run_topic_pubsub():
    context = {'counter': 0}
    ros_client = Ros('127.0.0.1', 9090)
    listener = Topic(ros_client, '/chatter', 'std_msgs/String')
    publisher = Topic(ros_client, '/chatter', 'std_msgs/String')

    def receive_message(message):
        context['counter'] += 1
        assert message['data'] == 'hello world', 'Unexpected message content'

        if context['counter'] == 3:
            listener.unsubscribe()
            # Give it a bit of time, just to make sure that unsubscribe
            # really unsubscribed and counter stays at the asserted value
            ros_client.call_later(2, ros_client.terminate)

    def start_sending():
        while True:
            if not ros_client.is_connected:
                break
            publisher.publish(Message({'data': 'hello world'}))
            time.sleep(0.1)
        publisher.unadvertise()

    def start_receiving():
        listener.subscribe(receive_message)

    ros_client.on_ready(start_receiving, run_in_thread=True)
    ros_client.on_ready(start_sending, run_in_thread=True)
    ros_client.run_forever()

    assert context['counter'] >= 3, 'Expected at least 3 messages but got ' + str(context['counter'])


def test_topic_pubsub():
    helpers.run_as_process(run_topic_pubsub)


if __name__ == '__main__':
    import logging

    logging.basicConfig(level=logging.DEBUG, format='[%(thread)03d] %(asctime)-15s [%(levelname)s] %(message)s')
    LOGGER = logging.getLogger('test')

    run_topic_pubsub()
