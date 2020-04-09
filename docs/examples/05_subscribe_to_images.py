import base64
import logging
import time

import roslibpy

# Configure logging
fmt = '%(asctime)s %(levelname)8s: %(message)s'
logging.basicConfig(format=fmt, level=logging.INFO)
log = logging.getLogger(__name__)

client = roslibpy.Ros(host='127.0.0.1', port=9090)

def receive_image(msg):
    log.info('Received image seq=%d', msg['header']['seq'])
    base64_bytes = msg['data'].encode('ascii')
    image_bytes = base64.b64decode(base64_bytes)
    with open('received-image-{}.{}'.format(msg['header']['seq'], msg['format']) , 'wb') as image_file:
        image_file.write(image_bytes)

subscriber = roslibpy.Topic(client, '/camera/image/compressed', 'sensor_msgs/CompressedImage')
subscriber.subscribe(receive_image)

client.run_forever()
