from __future__ import print_function

import time

import helpers

from roslibpy import Ros


def run_reconnect_does_not_trigger_on_client_close():
    ros = Ros('127.0.0.1', 9090)
    ros.run()

    assert ros.is_connected == True, "ROS initially connected"
    time.sleep(0.5)
    ros.close()
    time.sleep(0.5)

    assert ros.is_connected == False, "Successful disconnect"
    assert ros.is_connecting == False, "Not trying to re-connect"


def test_reconnect_does_not_trigger_on_client_close():
    helpers.run_as_process(run_reconnect_does_not_trigger_on_client_close)


if __name__ == '__main__':
    import logging

    logging.basicConfig(level=logging.INFO, format='[%(thread)03d] %(asctime)-15s [%(levelname)s] %(message)s')
    LOGGER = logging.getLogger('test')

    run_reconnect_does_not_trigger_on_client_close()
