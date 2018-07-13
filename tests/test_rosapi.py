import time

import helpers

from roslibpy import Ros


def run_rosapi_topics():
    ros_client = Ros('127.0.0.1', 9090)

    def callback(topic_list):
        print(topic_list)
        assert('/rosout' in topic_list['topics'])
        time.sleep(1)
        ros_client.terminate()

    def get_topics():
        ros_client.get_topics(callback)

    ros_client.on_ready(get_topics)
    ros_client.run_forever()


def test_rosapi_topics():
    helpers.run_as_process(run_rosapi_topics)


if __name__ == '__main__':
    import logging

    logging.basicConfig(level=logging.DEBUG, format='[%(thread)03d] %(asctime)-15s [%(levelname)s] %(message)s')
    LOGGER = logging.getLogger('test')

    run_rosapi_topics()
