import time

import roslibpy

client = roslibpy.Ros(host='localhost', port=9090)
talker = roslibpy.Topic(client, '/chatter', 'std_msgs/String')


def start_talking():
    while client.is_connected:
        talker.publish(roslibpy.Message({'data': 'Hello World!'}))
        print('Sending message...')
        time.sleep(1)

    talker.unadvertise()


client.on_ready(start_talking)
client.run_forever()
