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
Let's check the status::

    >>> ros.is_connected
    True

**Yay! Our first connection to ROS!**

Putting it all together
-----------------------

Let's build a full example into a python file. Create a file named
``ros-hello-world.py`` and paste the following content:

.. literalinclude :: files/ros-hello-world.py
   :language: python

Now run it from the command line typing::

    $ python ros-hello-world.py

The program will run, print once we are connected and terminate the connection.

Controlling the event loop
--------------------------

In the previous examples, we started the ROS connection with a call to ``run()``,
which starts the event loop in the background. In some case, we want handle the
main event loop more explicitely in the foreground.

:class:`roslibpy.Ros` provides the method ``run_forever()`` for this purpose.

If we use this method to start the event loop, we need to setup all connection handlers
before hand. We will use the :meth:`roslibpy.Ros.on_ready` method to do this.
We will pass a function to it, that will be invoked when the connection is ready.

The following snippet shows the same connection example above but
using ``run_forever()`` and ``on_ready``:

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

.. literalinclude :: files/ros-service-call-logger.py
   :language: python

* :download:`ros-service-call-logger.py <files/ros-service-call-logger.py>`

Creating services
-----------------

It is also possible to create new services, as long as the service type
definition is present in your ROS environment.

The following example shows how to create a simple service that uses
one of the standard service types defined in ROS (``std_srvs/SetBool``):

.. literalinclude :: files/ros-service.py
   :language: python

* :download:`ros-service.py <files/ros-service.py>`

Download it and run it from the command line typing::

    $ python ros-service.py

The service will be active while the program is running (to terminate,
press ``ctrl+c``).

Leave this service running and download and run the following service calling
code example to verify the service is working:

* :download:`ros-service-call-set-bool.py <files/ros-service-call-set-bool.py>`

Download it and run it from the command line typing::

    $ python ros-service-call-set-bool.py


.. note::

    Now that you have a grasp of the basics of ``roslibpy``,
    check out more details in the :ref:`ros-api-reference`.
