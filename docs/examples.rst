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

Controlling the event loop
--------------------------

In the previous examples, we have always used a call to ``run_forever()``
to kick start the event loop and block there until the connection is terminated.
This works fine in many scenarios, in particular, console applications, but
if you want to use a ROS client from an application that controls the event
loop already, you want to use the ``run()`` function instead.

Using ``run()`` starts the event processing just as ``run_forever()`` but
does not block the calling thread.

Hello World: Topics
-------------------

The ``Hello world`` of ROS is to start two nodes that communicate using
topic subscription/publishing. The nodes (a talker and a listener) are
extremely simple but they exemplify a distributed system with communication
between two processes over the ROS infrastructure.

Writing the talker node
^^^^^^^^^^^^^^^^^^^^^^^

The following example starts a ROS node and begins to publish
messages in loop (to terminate, press ``ctrl+c``):

.. literalinclude :: files/ros-hello-world-talker.py
   :language: python

Writing the listener node
^^^^^^^^^^^^^^^^^^^^^^^^^

Now let's move on to the listener side:

.. literalinclude :: files/ros-hello-world-listener.py
   :language: python

Running the example
^^^^^^^^^^^^^^^^^^^

Open a command prompt and start the talker:

::

    python ros-hello-world-talker.py


Now open a second command prompt and start the listener:

::

    python ros-hello-world-listener.py


.. note::

    It is not relevant where the files are located. They can be in different
    folders or even in different computers as long as the ROS master is the same.

