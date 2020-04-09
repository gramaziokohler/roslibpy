import time
import logging

import roslibpy

# Configure logging
fmt = '%(asctime)s %(levelname)8s: %(message)s'
logging.basicConfig(format=fmt, level=logging.INFO)
log = logging.getLogger(__name__)

client = roslibpy.Ros(host='127.0.0.1', port=9090)

def to_epoch(stamp):
    stamp_secs = stamp['secs']
    stamp_nsecs = stamp['nsecs']
    return stamp_secs + stamp_nsecs*1e-9

def from_epoch(stamp):
    stamp_secs = int(stamp)
    stamp_nsecs = (stamp - stamp_secs) * 1e9
    return {'secs': stamp_secs, 'nsecs': stamp_nsecs}

def receive_message(msg):
    age = time.time() - to_epoch(msg['stamp'])
    fmt = 'Age of message (sequence #%d): %6.3f seconds'
    log.info(fmt, msg['seq'], age)
    # Simulate a very slow consumer
    time.sleep(.5)

publisher = roslibpy.Topic(client, '/slow_consumer', 'std_msgs/Header')
publisher.advertise()

# Queue length needs to be used in combination with throttle rate (in ms)
# This value must be tuned to the expected duration of the slow consumer
# and ideally bigger than the max of it,
# otherwise message will be older than expected (up to a limit)
subscriber = roslibpy.Topic(client, '/slow_consumer', 'std_msgs/Header',
                            queue_length=1, throttle_rate=600)
subscriber.subscribe(receive_message)

seq = 0
def publish_message():
    global seq
    seq += 1
    header = dict(frame_id='', seq=seq, stamp=from_epoch(time.time()))
    publisher.publish(header)
    client.call_later(.001, publish_message)

client.on_ready(publish_message)
client.run_forever()
