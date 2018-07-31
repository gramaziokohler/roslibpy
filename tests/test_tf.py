import helpers

from roslibpy import Ros
from roslibpy.tf import TFClient


def run_tf_test():
    ros_client = Ros('127.0.0.1', 9090)
    tf_client = TFClient(ros_client, fixed_frame='world')

    def callback(message):
        assert message['translation'] == dict(x=0.0, y=0.0, z=0.0), 'Unexpected translation received'
        assert message['rotation'] == dict(x=0.0, y=0.0, z=0.0, w=1.0), 'Unexpected rotation received'
        ros_client.terminate()

    tf_client.subscribe(frame_id='/world', callback=callback)

    ros_client.call_later(2, ros_client.terminate)
    ros_client.run_forever()


def test_tf_test():
    helpers.run_as_process(run_tf_test)


if __name__ == '__main__':
    import logging

    logging.basicConfig(
        level=logging.DEBUG, format='[%(thread)03d] %(asctime)-15s [%(levelname)s] %(message)s')

    run_tf_test()
