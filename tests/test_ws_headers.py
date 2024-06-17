from __future__ import print_function
import threading
import time

from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory
from twisted.internet import reactor

from roslibpy import Ros

headers = {
    'cookie': 'token=rosbridge',
    'authorization': 'Some auth'
}

class TestWebSocketServerProtocol(WebSocketServerProtocol):
    def onConnect(self, request):
        for key, value in headers.items():
            assert request.headers.get(key) == value, f"Header {key} did not match expected value {value}"
        self.factory.context['wait'].set()

    def onOpen(self):
        self.sendClose()

def run_server(context):
    factory = WebSocketServerFactory()
    factory.protocol = TestWebSocketServerProtocol
    factory.context = context

    reactor.listenTCP(9000, factory)
    reactor.run(installSignalHandlers=False)

def run_client():
    client = Ros('127.0.0.1', 9000, headers=headers)
    client.run()
    client.close()

def test_websocket_headers():
    context = dict(wait=threading.Event())

    server_thread = threading.Thread(target=run_server, args=(context,))
    server_thread.start()

    time.sleep(1)  # Give the server time to start

    client_thread = threading.Thread(target=run_client)
    client_thread.start()

    if not context["wait"].wait(10):
        raise Exception("Headers were not as expected")

    client_thread.join()
    reactor.callFromThread(reactor.stop)
    server_thread.join()

if __name__ == "__main__":
    test_websocket_headers()
