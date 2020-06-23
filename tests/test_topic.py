from __future__ import print_function

import threading
import time

from roslibpy import Message
from roslibpy import Ros
from roslibpy import Topic


def test_topic_pubsub():
    context = dict(wait=threading.Event(), counter=0)

    ros = Ros('127.0.0.1', 9090)
    ros.run()

    listener = Topic(ros, '/chatter', 'std_msgs/String')
    publisher = Topic(ros, '/chatter', 'std_msgs/String')

    def receive_message(message):
        context['counter'] += 1
        assert message['data'] == 'hello world', 'Unexpected message content'

        if context['counter'] == 3:
            listener.unsubscribe()
            context['wait'].set()

    def start_sending():
        while True:
            if context['counter'] >= 3:
                break
            publisher.publish(Message({'data': 'hello world'}))
            time.sleep(0.1)
        publisher.unadvertise()

    def start_receiving():
        listener.subscribe(receive_message)

    t1 = threading.Thread(target=start_receiving)
    t2 = threading.Thread(target=start_sending)

    t1.start()
    t2.start()

    if not context['wait'].wait(10):
        raise Exception

    t1.join()
    t2.join()

    assert context['counter'] >= 3, 'Expected at least 3 messages but got ' + str(context['counter'])
    ros.close()
