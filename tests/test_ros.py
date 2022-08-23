from __future__ import print_function

import threading
import time

from roslibpy import Ros

host = "127.0.0.1"
port = 9090
url = "ws://%s:%d" % (host, port)


def test_reconnect_does_not_trigger_on_client_close():
    ros = Ros(host, port)
    ros.run()

    assert ros.is_connected, "ROS initially connected"
    time.sleep(0.5)
    event = threading.Event()
    ros.on("close", lambda m: event.set())
    ros.close()
    event.wait(5)

    assert not ros.is_connected, "Successful disconnect"
    assert not ros.is_connecting, "Not trying to re-connect"


def test_connection():
    ros = Ros(host, port)
    ros.run()
    assert ros.is_connected
    ros.close()


def test_url_connection():
    ros = Ros(url)
    ros.run()
    assert ros.is_connected
    ros.close()


def test_closing_event():
    ros = Ros(url)
    ros.run()
    ctx = dict(closing_event_called=False, was_still_connected=False)

    def handle_closing():
        ctx["closing_event_called"] = True
        ctx["was_still_connected"] = ros.is_connected
        time.sleep(1.5)

    ts_start = time.time()
    ros.on("closing", handle_closing)
    ros.close()
    ts_end = time.time()
    closing_was_handled_synchronously_before_close = ts_end - ts_start >= 1.5

    assert ctx["closing_event_called"]
    assert ctx["was_still_connected"]
    assert closing_was_handled_synchronously_before_close
