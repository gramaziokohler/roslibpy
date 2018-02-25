from __future__ import print_function

import helpers

from roslibpy import Ros, Service, ServiceRequest


def run_add_two_ints_service():
    ros_client = Ros('127.0.0.1', 9090)
    service = Service(ros_client, '/test_server',
                      'rospy_tutorials/AddTwoInts')

    def dispose_server():
        service.unadvertise()
        service.ros.call_later(1, service.ros.terminate)

    def add_two_ints(request, response):
        response['sum'] = request['a'] + request['b']
        if response['sum'] == 42:
            service.ros.call_later(2, dispose_server)

        return True

    def check_sum(result):
        assert(result['sum'] == 42)

    def invoke_service():
        client = Service(ros_client, '/test_server',
                         'rospy_tutorials/AddTwoInts')
        client.call(ServiceRequest({'a': 2, 'b': 40}), check_sum, print)

    service.advertise(add_two_ints)
    ros_client.call_later(1, invoke_service)
    ros_client.run_event_loop()


def test_add_two_ints_service():
    helpers.run_as_process(run_add_two_ints_service)
