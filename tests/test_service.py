from __future__ import print_function

import time

import helpers

from roslibpy import Ros
from roslibpy import Service
from roslibpy import ServiceRequest


def run_add_two_ints_service():
    ros_client = Ros('127.0.0.1', 9090)
    ros_client.run()

    def add_two_ints(request, response):
        response['sum'] = request['a'] + request['b']

        return False

    service_name = '/test_sum_service'
    service_type = 'rospy_tutorials/AddTwoInts'
    service = Service(ros_client, service_name, service_type)
    service.advertise(add_two_ints)
    time.sleep(1)

    client = Service(ros_client, service_name, service_type)
    result = client.call(ServiceRequest({'a': 2, 'b': 40}))
    assert(result['sum'] == 42)

    service.unadvertise()
    time.sleep(2)
    service.ros.terminate()


def run_empty_service():
    ros_client = Ros('127.0.0.1', 9090)
    ros_client.run()

    service = Service(ros_client, '/test_empty_service', 'std_srvs/Empty')
    service.advertise(lambda req, resp: True)
    time.sleep(1)

    client = Service(ros_client, '/test_empty_service', 'std_srvs/Empty')
    client.call(ServiceRequest())

    service.unadvertise()
    time.sleep(2)
    service.ros.terminate()


def test_add_two_ints_service():
    helpers.run_as_process(run_add_two_ints_service)


def test_empty_service():
    helpers.run_as_process(run_empty_service)


if __name__ == '__main__':
    import logging

    logging.basicConfig(
        level=logging.INFO, format='[%(thread)03d] %(asctime)-15s [%(levelname)s] %(message)s')
    LOGGER = logging.getLogger('test')

    run_add_two_ints_service()
    # run_empty_service()
