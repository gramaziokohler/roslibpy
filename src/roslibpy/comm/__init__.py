import sys

from .comm import RosBridgeException, RosBridgeProtocol

if sys.platform == 'cli':
    raise NotImplementedError()
else:
    from .comm_autobahn import AutobahnRosBridgeClientFactory as RosBridgeClientFactory

__all__ = ['RosBridgeException', 'RosBridgeProtocol', 'RosBridgeClientFactory']
