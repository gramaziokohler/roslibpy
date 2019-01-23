
Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <http://keepachangelog.com/en/1.0.0/>`_
and this project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`_.

Unreleased
----------

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
