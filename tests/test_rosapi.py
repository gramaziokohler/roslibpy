import helpers
import pytest

from roslibpy import Ros

host = '127.0.0.1'
port = 9090
url = u'ws://%s:%d' % (host, port)


def run_rosapi_topics(*args, **kwargs):
    ros_client = Ros(*args, **kwargs)

    def callback(topic_list):
        assert('/rosout' in topic_list['topics'])
        ros_client.terminate()

    def get_topics():
        ros_client.get_topics(callback)

    ros_client.on_ready(get_topics)
    ros_client.run_event_loop()


def test_rosapi_topics():
    helpers.run_as_process(run_rosapi_topics, host, port)


def test_rosapi_topics_url():
    helpers.run_as_process(run_rosapi_topics, url)


def test_connection_url_checks():
    with pytest.raises(Exception):
        helpers.run_as_process(Ros, host)

    with pytest.raises(Exception):
        helpers.run_as_process(Ros, u'http://%s:%d' % (host, port))
