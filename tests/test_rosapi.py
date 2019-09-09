import time

import helpers

from roslibpy import Ros

host = '127.0.0.1'
port = 9090
url = u'ws://%s:%d' % (host, port)


def run_rosapi_topics(*args, **kwargs):
    ros_client = Ros(*args, **kwargs)

    def callback(topic_list):
        print(topic_list)
        assert('/rosout' in topic_list['topics'])
        time.sleep(1)
        ros_client.terminate()

    def get_topics():
        ros_client.get_topics(callback)

    ros_client.on_ready(get_topics)
    ros_client.run_forever()


def run_rosapi_topics_blocking(*args, **kwargs):
    ros_client = Ros(*args, **kwargs)
    ros_client.run()
    topic_list = ros_client.get_topics()

    print(topic_list)
    assert('/rosout' in topic_list)

    ros_client.terminate()


def test_rosapi_topics():
    helpers.run_as_process(run_rosapi_topics, host, port)


def test_rosapi_topics_blocking():
    helpers.run_as_process(run_rosapi_topics_blocking, host, port)


def test_rosapi_topics_url():
    helpers.run_as_process(run_rosapi_topics, url)


def test_connection_url_checks():
    import pytest
    with pytest.raises(Exception):
        helpers.run_as_process(Ros, host)

    with pytest.raises(Exception):
        helpers.run_as_process(Ros, u'http://%s:%d' % (host, port))


if __name__ == '__main__':
    import logging

    logging.basicConfig(level=logging.INFO, format='[%(thread)03d] %(asctime)-15s [%(levelname)s] %(message)s')
    LOGGER = logging.getLogger('test')

    run_rosapi_topics(host, port)
