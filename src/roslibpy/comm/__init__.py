import sys

from .comm import RosBridgeException, RosBridgeProtocol

if sys.platform == "cli":
    from .comm_cli import CliRosBridgeClientFactory as RosBridgeClientFactory
else:
    from .comm_autobahn import AutobahnRosBridgeClientFactory as RosBridgeClientFactory

__all__ = ["RosBridgeException", "RosBridgeProtocol", "RosBridgeClientFactory"]
