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
import logging

listeners = {}

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', filename='/var/log/emojiserver.log',level=logging.INFO)
logger = logging.getLogger(__name__)

class MyServerProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        logger.info("Client connecting: {0}".format(request.peer))

    def onOpen(self):
        logger.info("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        if isBinary:
            logger.info("Binary message received: {0} bytes".format(len(payload)))
        else:
	    if (payload.decode('utf8')[:6] == "listen"):
		listeners[payload.decode('utf8')[7:]] = self
		logger.info("added listener " + payload.decode('utf8')[7:])
	    else:
        	emojido = json.loads(payload.decode('utf8'))
		logger.info("Command received: {0}".format(str(emojido)))
		try:
		    listeners[emojido["channel"]].sendMessage(payload, isBinary)
		except:
		    logger.info("Couldn't find listener" + emojido["channel"])
                
		#for l in listeners.values():
		#    l.sendMessage(payload, isBinary)

    def onClose(self, wasClean, code, reason):
        logger.info("WebSocket connection closed: {0}".format(reason))
	for i in range(len(listeners.values())):
	    if (listeners.values()[i] == self):
		del listeners[listeners.key()[i]]
		break

if __name__ == '__main__':

    import sys

    from twisted.python import log
    from twisted.internet import reactor

    #log.startLogging(open("/var/log/emojiserver.log", "w"))
    observer = log.PythonLoggingObserver()
    observer.start()

    factory = WebSocketServerFactory(u"ws://127.0.0.1:9000")
    factory.protocol = MyServerProtocol
    factory.setProtocolOptions(autoPingInterval=5, autoPingTimeout=2)
    # factory.setProtocolOptions(maxConnections=2)

    # note to self: if using putChild, the child must be bytes...

    reactor.listenTCP(9000, factory)
    reactor.run()

