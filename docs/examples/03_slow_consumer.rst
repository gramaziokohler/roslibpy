Throttle messages for a slow consumer
=====================================

This example shows how to throttle messages that are published are a rate faster than
what a slow consumer (subscribed) can process. In this example, only the newest messages
are preserved, messages that cannot be consumed on time are dropped.

.. literalinclude :: 03_slow_consumer.py
   :language: python

In the console, you should see gaps in the sequence of messages, because the publisher is
producing messages every 0.001 seconds, but we configure a queue of length 1, with a
throttling of 600ms to give time to our slow consumer. Without this throttling, the consumer
would process increasingly old messages.
