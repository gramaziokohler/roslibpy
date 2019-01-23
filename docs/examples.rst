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

We start importing ``roslibpy`` as follows::

    >>> import roslibpy

And we initialize the connection with::

    >>> ros = roslibpy.Ros(host='localhost', port=9090)
    >>> ros.run()

Easy, right?

The previous lines start connecting but do not block, i.e. the connection is
established in the background but the functions returns the control to the
program immediately.

Let's check the status::

    >>> ros.is_connected
    True

**Yay! Our first connection to ROS!**

Waiting for connection
----------------------

The previous example works fine because we are typing it on the interpreter and
that is -usually- slow enough for the connection to be established, but
when writing a script you will want to make sure that your code reacts
when the connection is really ready.

For that we will use the :meth:`roslibpy.Ros.on_ready` method and pass a function
(or a lambda) that we want to be invoked when the connection is ready.

Here we will simply print whether we are connected, but you can do any
other ROS operation in there, such as subscribing to a topic,
or calling services, etc::

    ros.on_ready(lambda: print('Is ROS connected?', ros.is_connected))

Putting it all together
-----------------------

Let's build a full example into a python file. Create a file named
``ros-hello-world.py`` and paste the following content:

.. literalinclude :: files/ros-hello-world.py
   :language: python

Now run it from the command line typing::

    $ python ros-hello-world.py

The program will run, print once we are connected and wait there forever.
To interrupt and return to the console, please ``ctrl+c``.

Controlling the event loop
--------------------------

In the previous examples, we started the ROS connection with a call to ``run()``,
but sometimes we want to let ``roslibpy`` take care of the main
event loop. In those cases, it is easier to call ``run_forever()`` instead.

The following snippet shows the same connection example above but
using ``run_forever()``:

.. literalinclude :: files/ros-hello-world-run-forever.py
   :language: python

.. note::

    The difference between ``run()`` and ``run_forever()`` is that the former
    starts the event processing in a separate thread, while the latter
    blocks the calling thread.

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

* :download:`ros-hello-world-talker.py <files/ros-hello-world-talker.py>`

Writing the listener node
^^^^^^^^^^^^^^^^^^^^^^^^^

Now let's move on to the listener side:

.. literalinclude :: files/ros-hello-world-listener.py
   :language: python

* :download:`ros-hello-world-listener.py <files/ros-hello-world-listener.py>`

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


Using services
--------------

Another way for nodes to communicate between each other is through ROS Services.

Services require the definition of request and response types so the following
example shows how to use an existing service called ``get_loggers``:

.. literalinclude :: files/ros-service-caller.py
   :language: python

* :download:`ros-service-caller.py <files/ros-service-caller.py>`
