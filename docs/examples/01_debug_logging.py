import logging

import roslibpy

# Configure logging to high verbosity (DEBUG)
fmt = '%(asctime)s %(levelname)8s: %(message)s'
logging.basicConfig(format=fmt, level=logging.DEBUG)
log = logging.getLogger(__name__)

client = roslibpy.Ros(host='127.0.0.1', port=9090)
client.on_ready(lambda: log.info('On ready has been triggered'))

client.run_forever()
