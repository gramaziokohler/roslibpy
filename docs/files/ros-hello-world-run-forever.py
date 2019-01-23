from __future__ import print_function
import roslibpy

ros = roslibpy.Ros(host='localhost', port=9090)
ros.on_ready(lambda: print('Is ROS connected?', ros.is_connected))
ros.run_forever()
