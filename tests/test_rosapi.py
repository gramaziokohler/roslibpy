import threading

import pytest

from roslibpy import Ros

host = '127.0.0.1'
port = 9090
url = u'ws://%s:%d' % (host, port)


def test_rosapi_topics():
    context = dict(wait=threading.Event(), result=None)
    ros = Ros(host, port)
    ros.run()

    def callback(topic_list):
        context['result'] = topic_list
        context['wait'].set()

    ros.get_topics(callback)
    if not context['wait'].wait(5):
        raise Exception

    assert('/rosout' in context['result']['topics'])
    ros.close()


def test_rosapi_topics_blocking():
    ros = Ros(host, port)
    ros.run()
    topic_list = ros.get_topics()

    print(topic_list)
    assert('/rosout' in topic_list)

    ros.close()


def test_connection_fails_when_missing_port():
    with pytest.raises(Exception):
        Ros(host)


def test_connection_fails_when_schema_not_ws():
    with pytest.raises(Exception):
        Ros(u'http://%s:%d' % (host, port))
