#!/usr/bin/env python
# -*- coding: UTF-8 -*-# enable debugging
import cgitb
import cgi
import sys, os
import json
import re
from slackclient import SlackClient
import emojiconfig as config

cgitb.enable()    

sc = SlackClient(config.slacktoken)

with open('/home/romirez/emoji.json') as data_file:    
    emoji = json.load(data_file)

print("Content-Type: text/html;charset=utf-8")
print    
fs = cgi.FieldStorage()

el = sc.api_call(
  "emoji.list"
)["emoji"]

emojido = {}

senttext = fs.getvalue("text")
if senttext == "off":
	emojido["command"] = "off"
elif senttext[:10] == "brightness":
	emojido["command"] = "brightness"
	try:
		emojido["value"] = int(senttext[11:])
	except:
		emojido = {}
elif senttext[:4] == "text":
	emojido["command"] = "text"
	emojido["value"] = senttext[5:]
elif senttext[:3] == "url":
	emojido["command"] = "image"
	emojido["value"] = senttext[4:]
else:
	sentemoji = re.search("\:(.*?)\:", fs.getvalue("text")).group(0)[1:-1:]

	emjfile = ""

	try:
		normem = (item for item in emoji if item["short_name"] == sentemoji).next()
		emjfile = "https://raw.githubusercontent.com/iamcal/emoji-data/master/img-apple-64/" + normem["image"]
	except:
		emjfile = el[sentemoji]
	
	emojido["command"] = "image"
	emojido["value"] = emjfile

f = open("/var/www/html/emoji.txt","w")
r = ""

#f.write(str(fs.getvalue("text")))
#f.write(str(el) + "\n")
#f.write(sentemoji + "\n")
#filename = str((item for item in emoji if item["short_name"] == sentemoji).next()["image"])
f.write(str(emojido))

f.close()

from autobahn.twisted.websocket import WebSocketClientProtocol, \
    WebSocketClientFactory

class MyClientProtocol(WebSocketClientProtocol):
    def onOpen(self):
        self.sendMessage(json.dumps(emojido).encode('utf8'))
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

