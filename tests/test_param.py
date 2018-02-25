import helpers

from roslibpy import Param, Ros


def run_param_manipulation():
    ros_client = Ros('127.0.0.1', 9090)

    def delete_param_done(_):
        ros_client._test_param_del = True

    def get_param_done(value):
        ros_client._test_param_value = value

        delete_param = Param(ros_client, 'test_param')
        delete_param.delete(delete_param_done)

    def set_param_done(_):
        ros_client._test_param_set = True

        check_param = Param(ros_client, 'test_param')
        check_param.get(get_param_done)

    param = Param(ros_client, 'test_param')
    param.set('test_value', set_param_done)

    def verify():
        assert(ros_client._test_param_set is True)
        assert(ros_client._test_param_value == 'test_value')
        assert(ros_client._test_param_del is True)
        ros_client.terminate()

    ros_client.call_later(1, verify)
    ros_client.run_event_loop()


def test_param_manipulation():
    helpers.run_as_process(run_param_manipulation)
