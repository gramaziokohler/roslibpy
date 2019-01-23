from __future__ import print_function
import roslibpy

ros = roslibpy.Ros(host='localhost', port=9090)

ros.run()
ros.on_ready(lambda: print('Is ROS connected?', ros.is_connected))

try:
    while True:
        pass
except KeyboardInterrupt:
    pass

ros.terminate()
