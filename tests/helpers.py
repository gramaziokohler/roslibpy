"""Everything in this module is horrible."""

import multiprocessing
import traceback


class Process(multiprocessing.Process):
    """Horrible workaround for the fact that Twisted reactors cannot be restarted."""

    def __init__(self, *args, **kwargs):
        multiprocessing.Process.__init__(self, *args, **kwargs)
        self._pconn, self._cconn = multiprocessing.Pipe()
        self._exception = None

    def run(self):
        try:
            multiprocessing.Process.run(self)
            self._cconn.send(None)
        except Exception as e:
            tb = traceback.format_exc()
            self._cconn.send((e, tb))

    @property
    def exception(self):
        if self._pconn.poll():
            self._exception = self._pconn.recv()
        return self._exception


def run_as_process(func, *args, **kwargs):
    p = Process(target=func, args=args, kwargs=kwargs)
    p.start()
    p.join()

    if p.exception:
        error, _ = p.exception
        raise(error)
