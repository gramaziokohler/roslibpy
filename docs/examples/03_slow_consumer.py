import time
import logging

from roslibpy import Header
from roslibpy import Ros
from roslibpy import Time
from roslibpy import Topic
from roslibpy.core import LOGGER

# Configure logging
fmt = '%(asctime)s %(levelname)8s: %(message)s'
logging.basicConfig(format=fmt, level=logging.INFO)
log = logging.getLogger(__name__)

client = Ros(host='127.0.0.1', port=9090)

def receive_message(msg):
    header = Header(msg['seq'], msg['stamp'], msg['frame_id'])
    age = time.time() - header['stamp'].to_sec()
    fmt = 'Age of message (sequence #%d): %6.3f seconds'
    log.info(fmt, msg['seq'], age)
    # Simulate a very slow consumer
    time.sleep(.5)

publisher = Topic(client, '/slow_consumer', 'std_msgs/Header')
publisher.advertise()

# Queue length needs to be used in combination with throttle rate (in ms)
# This value must be tuned to the expected duration of the slow consumer
# and ideally bigger than the max of it,
# otherwise message will be older than expected (up to a limit)
subscriber = Topic(client, '/slow_consumer', 'std_msgs/Header',
                            queue_length=1, throttle_rate=600)
subscriber.subscribe(receive_message)

seq = 0
def publish_message():
    global seq
    seq += 1
    header = Header(frame_id='', seq=seq, stamp=Time.now())
    publisher.publish(header)
    client.call_later(.001, publish_message)

client.on_ready(publish_message)
client.run_forever()
