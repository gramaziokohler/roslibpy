# -*- coding: utf-8 -*-

# The following code is derivative work of [pyee](https://github.com/jfhbrook/pyee)
# Copyrighted by Joshua Holbrook with a MIT license


# The MIT License(MIT)

# Copyright(c) 2015 Joshua Holbrook

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files(the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and / or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
``EventEmitterMixin`` is similar to the ``EventEmitter`` of Node.js.
It supports both synchronous callbacks and asyncio coroutines.
"""

try:
    from asyncio import ensure_future
    from asyncio import iscoroutine
except ImportError:
    iscoroutine = None
    ensure_future = None

from collections import OrderedDict
from collections import defaultdict
from threading import RLock

__all__ = ["EventEmitterMixin", "EventEmitterException"]


class EventEmitterException(Exception):
    """An internal exception."""

    pass


class EventEmitterMixin(object):
    """Mixin to add event emitter features to a class.

    For interoperation with asyncio, one can specify the scheduler and
    the event loop. The scheduler defaults to ``asyncio.ensure_future``,
    and the loop defaults to ``None``. When used with the default scheduler,
    this will schedule the coroutine onto asyncio's default loop.

    This should also be compatible with recent versions of twisted by
    setting ``scheduler=twisted.internet.defer.ensureDeferred``.

    Most events are registered with EventEmitterMixin via the ``on`` and ``once``
    methods. However, event emitters have two *special* events:

    - ``new_listener``: Fires whenever a new listener is created. Listeners for
      this event do not fire upon their own creation.

    - ``error``: When emitted raises an Exception by default, behavior can be
      overriden by attaching callback to the event.

      For example::

          @ee.on('error')
          def onError(message):
              logging.err(message)

          ee.emit('error', Exception('something blew up'))

      For synchronous callbacks, exceptions are **not** handled for you---
      you must catch your own exceptions inside synchronous ``on`` handlers.
      However, when wrapping **async** functions, errors will be intercepted
      and emitted under the ``error`` event. **This behavior for async
      functions is inconsistent with node.js**, which unlike this package has
      no facilities for handling returned Promises from handlers.
    """

    def __init__(self, *args, **kwargs):
        super(EventEmitterMixin, self).__init__(*args, **kwargs)
        self._events = defaultdict(OrderedDict)
        self._schedule = kwargs.get("scheduler", ensure_future)
        self._loop = kwargs.get("loop", None)
        self._event_lock = RLock()

    def on(self, event, f=None):
        """Registers the function (or optionally an asyncio coroutine function)
        ``f`` to the event name ``event``.

        If ``f`` isn't provided, this method returns a function that
        takes ``f`` as a callback; in other words, you can use this method
        as a decorator, like so::

            @ee.on('data')
            def data_handler(data):
                print(data)

        As mentioned, this method can also take an asyncio coroutine function::

           @ee.on('data')
           async def data_handler(data)
               await do_async_thing(data)


        This will automatically schedule the coroutine using the configured
        scheduling function (defaults to ``asyncio.ensure_future``) and the
        configured event loop (defaults to ``asyncio.get_event_loop()``).

        In both the decorated and undecorated forms, the event handler is
        returned. The upshot of this is that you can call decorated handlers
        directly, as well as use them in remove_listener calls.
        """

        with self._event_lock:

            def _on(f):
                self._add_event_handler(event, f, f)
                return f

            if f is None:
                return _on
            else:
                return _on(f)

    def _add_event_handler(self, event, k, v):
        # Fire 'new_listener' *before* adding the new listener!
        self.emit("new_listener", event, k)

        # Add the necessary function
        # Note that k and v are the same for `on` handlers, but
        # different for `once` handlers, where v is a wrapped version
        # of k which removes itself before calling k
        self._events[event][k] = v

    def emit(self, event, *args, **kwargs):
        """Emit ``event``, passing ``*args`` and ``**kwargs`` to each attached
        function. Returns ``True`` if any functions are attached to ``event``;
        otherwise returns ``False``.

        Example::

            ee.emit('data', '00101001')

        Assuming ``data`` is an attached function, this will call
        ``data('00101001')'``.

        For coroutine event handlers, calling emit is non-blocking. In other
        words, you do not have to await any results from emit, and the
        coroutine is scheduled in a fire-and-forget fashion.
        """
        handled = False

        with self._event_lock:
            for f in list(self._events[event].values()):
                result = f(*args, **kwargs)

                # If f was a coroutine function, we need to schedule it and
                # handle potential errors
                if iscoroutine and iscoroutine(result):
                    if self._loop:
                        d = self._schedule(result, loop=self._loop)
                    else:
                        d = self._schedule(result)

                    # scheduler gave us an asyncio Future
                    if hasattr(d, "add_done_callback"):

                        @d.add_done_callback
                        def _callback(f):
                            exc = f.exception()
                            if exc:
                                self.emit("error", exc)

                    # scheduler gave us a twisted Deferred
                    elif hasattr(d, "addErrback"):

                        @d.addErrback
                        def _callback(exc):
                            self.emit("error", exc)

                handled = True

        if not handled and event == "error":
            if args:
                raise args[0]
            else:
                raise EventEmitterException("Uncaught, unspecified 'error' event.")

        return handled

    def once(self, event, f=None):
        """The same as ``ee.on``, except that the listener is automatically
        removed after being called.
        """

        with self._event_lock:

            def _wrapper(f):
                def g(*args, **kwargs):
                    self.remove_listener(event, f)
                    # f may return a coroutine, so we need to return that
                    # result here so that emit can schedule it
                    return f(*args, **kwargs)

                self._add_event_handler(event, f, g)
                return f

            if f is None:
                return _wrapper
            else:
                return _wrapper(f)

    def off(self, event, f):
        """Removes the function ``f`` from ``event``."""
        self._events[event].pop(f)

    def remove_listener(self, event, f):
        """Removes the function ``f`` from ``event``."""
        self._events[event].pop(f)

    def remove_all_listeners(self, event=None):
        """Remove all listeners attached to ``event``.
        If ``event`` is ``None``, remove all listeners on all events.
        """
        with self._event_lock:
            if event is not None:
                self._events[event] = OrderedDict()
            else:
                self._events = defaultdict(OrderedDict)

    def listeners(self, event):
        """Returns a list of all listeners registered to the ``event``."""
        return list(self._events[event].keys())
