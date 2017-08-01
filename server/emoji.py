#!/usr/bin/env python
# -*- coding: UTF-8 -*-# enable debugging
import cgitb
import cgi
import sys, os
import json
import re
from slackclient import SlackClient

cgitb.enable()    

sc = SlackClient("xoxp-2592814670-2836311839-218918329984-0c5c856149f63b423379977b96e3e0d6")

with open('/home/romirez/emoji.json') as data_file:    
    emoji = json.load(data_file)

print("Content-Type: text/html;charset=utf-8")
print    
fs = cgi.FieldStorage()

el = sc.api_call(
  "emoji.list"
)["emoji"]

senttext = fs.getvalue("text")
if senttext == "off":
	emjfile=""
else:
	sentemoji = re.search("\:(.*?)\:", fs.getvalue("text")).group(0)[1:-1:]

	emjfile = ""

	try:
		normem = (item for item in emoji if item["short_name"] == sentemoji).next()
		emjfile = "https://raw.githubusercontent.com/iamcal/emoji-data/master/img-apple-64/" + normem["image"]
	except:
		emjfile = el[sentemoji]

f = open("/var/www/html/emoji.txt","w")
r = ""

#f.write(str(fs.getvalue("text")))
#f.write(str(el) + "\n")
#f.write(sentemoji + "\n")
#filename = str((item for item in emoji if item["short_name"] == sentemoji).next()["image"])
f.write(emjfile)

f.close()

from autobahn.twisted.websocket import WebSocketClientProtocol, \
    WebSocketClientFactory

class MyClientProtocol(WebSocketClientProtocol):
    def onOpen(self):
        self.sendMessage(emjfile.encode('utf8'))
        self.sendClose()

from twisted.python import log
from twisted.internet import reactor

factory = WebSocketClientFactory(u"ws://127.0.0.1:9000")
factory.protocol = MyClientProtocol

reactor.connectTCP("127.0.0.1", 9000, factory)
reactor.run()

