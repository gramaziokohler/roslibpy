from __future__ import print_function
import roslibpy

ros = roslibpy.Ros(host='localhost', port=9090)
ros.run()
print('Is ROS connected?', ros.is_connected)
ros.terminate()
