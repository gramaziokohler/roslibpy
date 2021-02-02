Check roundtrip message latency
===============================

This example shows how to check roundtrip message latency on your system.

.. literalinclude :: 02_check_latency.py
   :language: python

The output on the console should look similar to the following::

    $ python 02_check_latency.py
    2020-04-09 07:45:49,909     INFO: Connection to ROS ready.
    2020-04-09 07:45:50,431     INFO: Age of message:      2ms
    2020-04-09 07:45:50,932     INFO: Age of message:      2ms
    2020-04-09 07:45:51,431     INFO: Age of message:      1ms
    2020-04-09 07:45:51,932     INFO: Age of message:      2ms
    2020-04-09 07:45:52,434     INFO: Age of message:      3ms
    2020-04-09 07:45:52,934     INFO: Age of message:      2ms
    2020-04-09 07:45:53,435     INFO: Age of message:      3ms
    2020-04-09 07:45:53,934     INFO: Age of message:      1ms
    2020-04-09 07:45:54,436     INFO: Age of message:      2ms
