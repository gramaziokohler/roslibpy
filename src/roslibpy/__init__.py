"""

This library relies on the `ROS bridge suite <http://wiki.ros.org/rosbridge_suite>`_
by Robot Web Tools to interact with ROS via WebSockets.

The `ROS bridge protocol <https://github.com/RobotWebTools/rosbridge_suite/blob/master/ROSBRIDGE_PROTOCOL.md>`_
uses JSON as message transport to allow access to ROS functionality such as
publishing, subscribing, service calls, actionlib, TF, etc.

.. _ros-setup:

ROS Setup
=========

In order to use this library, your ROS environment needs to be setup to run ``rosbridge``.

First install the **rosbridge suite** with the following commands::

    sudo apt-get install -y ros-kinetic-rosbridge-server
    sudo apt-get install -y ros-kinetic-tf2-web-republisher

And before starting a connection, make sure you launch all services::

    roslaunch rosbridge_server rosbridge_websocket.launch
    rosrun tf2_web_republisher tf2_web_republisher


Connecting to ROS
=================

The connection to ROS is managed by the :class:`Ros` class. Besides connection and
disposal, it handles automatic reconnections when needed.

Other classes that need an active connection with ROS receive this instance
as an argument to their constructors.

.. autoclass:: Ros
   :members:

Main ROS concepts
=================

Topics
------

ROS is a communication infrastructure. In ROS, different **nodes** communicate with
each other through messages. **ROS messages** are represented by the :class:`Message`
class and are passed around via :class:`Topics <Topic>` using a **publish/subscribe**
model.

.. autoclass:: Message
   :members:
.. autoclass:: Topic
   :members:

Services
--------

Besides the publish/subscribe model used with topics, ROS offers a request/response
model via :class:`Services <Service>`.

.. autoclass:: Service
   :members:
.. autoclass:: ServiceRequest
   :members:
.. autoclass:: ServiceResponse
   :members:


Parameter server
----------------

ROS provides a parameter server to share data among different nodes. This service
can be accessed via the :class:`Param` class.

.. autoclass:: Param
   :members:

"""

from .__version__ import __author__
from .__version__ import __author_email__
from .__version__ import __copyright__
from .__version__ import __description__
from .__version__ import __license__
from .__version__ import __title__
from .__version__ import __url__
from .__version__ import __version__
from .core import Message
from .core import Param
from .core import Service
from .core import ServiceRequest
from .core import ServiceResponse
from .core import Topic
from .ros import Ros

__all__ = ['Ros', 'Message', 'Param', 'Service', 'ServiceRequest', 'ServiceResponse', 'Topic', '__author__',
           '__author__', '__author_email__', '__copyright__', '__description__', '__license__', '__title__', '__url__', '__version__']
