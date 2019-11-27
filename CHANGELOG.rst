
Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <http://keepachangelog.com/en/1.0.0/>`_
and this project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`_.

0.7.1
----------

**Fixed**

* Fixed blocking service calls for Mac OS

0.7.0
----------

**Changed**

* The non-blocking event loop runner ``run()`` now defaults to 10 seconds timeout before raising an exception.

**Added**

* Added blocking behavior to ROS API methods, e.g. ``ros.get_topics``.
* Added command-line mode to ROS API, e.g. ``roslibpy topic list``.
* Added blocking behavior to the ``Param`` class.
* Added parameter manipulation methods to ``Ros`` class: ``get_param``, ``set_param``, ``delete_param``.

0.6.0
----------

**Changed**

* For consistency, ``timeout`` parameter of ``Goal.send()`` is now expressed in **seconds**, instead of milliseconds.

**Deprecated**

* The ``timeout`` parameter of ``ActionClient()`` is ignored in favor of blocking until the connection is established.

**Fixed**

* Raise exceptions when timeouts expire on ROS connection or service calls.

**Added**

* Support for calling a function in a thread from the Ros client.
* Added implementation of a Simple Action Server.

0.5.0
----------

**Changed**

* The non-blocking event loop runner now waits for the connection to be established in order to minimize the need for ``on_ready`` handlers.

**Added**

* Support blocking and non-blocking service calls.

**Fixed**

* Fixed an internal unsubscribing issue.

0.4.1
----------

**Fixed**

* Resolve reconnection issues.

0.4.0
----------

**Added**

* Add a non-blocking event loop runner

0.3.0
----------

**Changed**

* Unsubscribing from a listener no longer requires the original callback to be passed.

0.2.1
----------

**Fixed**

* Fix JSON serialization error on TF Client (on Python 3.x)

0.2.0
----------

**Added**

* Add support for IronPython 2.7

**Changed**

* Handler ``on_ready`` now defaults to run the callback in thread

**Deprecated**

* Rename ``run_event_loop`` to the more fitting ``run_forever``

0.1.1
----------

**Fixed**

* Minimal documentation fixes

0.1.0
----------

**Added**

* Initial version
