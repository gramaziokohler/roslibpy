Examples
========

Getting started with **roslibpy** is simple. The following examples will help you
on the first steps using it to connect to a ROS environment. Before you start, make sure
you have ROS and `rosbridge` running (see :ref:`ros-setup`).

These examples assume ROS is running on the same computer where you run the examples.
If that is not the case, change the ``host`` argument from ``'localhost'``
to the *IP Address* of your ROS master.

First connection
----------------

From a python interpreter, run the following lines one by one.
If you are on Python 2.x, the first import should be the `print_function`
from the future (on Python 3.x you can skip this line)::

    >>> from __future__ import print_function

Now we import `roslibpy` as follows::

    >>> import roslibpy

And we are ready to initialize the connection::

    >>> ros = roslibpy.Ros(host='localhost', port=9090)

Easy, right?

But we are not done. The previous line starts connecting but does not block, i.e.
the connection is established in the background but the functions returns the
control to the program immediately.

Next is to tell our program what to do once the connection is ready, for that
we will pass a function (or a lambda) to the ``on_ready`` handler. Here we will
simply print whether we are connected, but you can do any other ROS operation
in there, such as subscribing to a topic, or calling services, etc::

    >>> ros.on_ready(lambda: print('Is ROS connected?', ros.is_connected))

The connection is configured and now we can tell our program to run through it.
For that purpose we will call the `run_forever` function
that will wait blocking while we interact with ROS::

    >>> ros.run_forever()
    Is ROS connected? True

**Yay! Our first connection to ROS!**

Putting it all together
-----------------------

We can move the full example into a python file. Create a file named ``test-01.py``
and paste the following content::

    from __future__ import print_function
    import roslibpy

    ros = roslibpy.Ros(host='localhost', port=9090)
    ros.on_ready(lambda: print('Is ROS connected?', ros.is_connected))
    ros.run_forever()

Now run it from the command line typing::

    $ python test-01.py

The program will run, print once we are connected and wait there forever.
To interrupt and return to the console, please ``ctrl+c``.
