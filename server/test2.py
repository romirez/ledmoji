import json
from autobahn.twisted.websocket import WebSocketClientProtocol, \
    WebSocketClientFactory

class MyClientProtocol(WebSocketClientProtocol):
    def onOpen(self):
        self.sendMessage(json.dumps({}).encode('utf8'))
        self.sendClose()

    def onClose(self, wasClean, code, reason):
        from twisted.internet import reactor
        reactor.callFromThread(reactor.stop)

from twisted.python import log
from twisted.internet import reactor

factory = WebSocketClientFactory(u"ws://127.0.0.1:9000")
factory.protocol = MyClientProtocol

reactor.connectTCP("127.0.0.1", 9000, factory)
reactor.run()
