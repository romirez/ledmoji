#!/usr/bin/env python
# -*- coding: UTF-8 -*-# enable debugging
import cgitb
import cgi
import sys, os
import json
import re
from slackclient import SlackClient
from autobahn.twisted.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory

listeners = []

class MyServerProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))

    def onOpen(self):
        print("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
	    if (payload.decode('utf8') == "listen"):
		listeners.append(self)
		print("added listener")
	    else:
	        print("Text message received: {0}".format(payload.decode('utf8')))
        	emojido = json.loads(payload.decode('utf8'))
                print("emojido: " + str(emojido))
                for l in listeners:
		    l.sendMessage(payload, isBinary)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))
	for i in range(len(listeners)):
	    if (listeners[i] == self):
		listeners.remove(i)
		break

if __name__ == '__main__':

    import sys

    from twisted.python import log
    from twisted.internet import reactor

    log.startLogging(sys.stdout)

    factory = WebSocketServerFactory(u"ws://127.0.0.1:9000")
    factory.protocol = MyServerProtocol
    # factory.setProtocolOptions(maxConnections=2)

    # note to self: if using putChild, the child must be bytes...

    reactor.listenTCP(9000, factory)
    reactor.run()

