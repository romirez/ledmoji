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

emojido["username"] = fs.getvalue("user_name");
emojido["channel"] = fs.getvalue("channel_name");

senttext = fs.getvalue("text")
if senttext == None:
	senttext = ""

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
elif senttext[:4] == "demo":
	emojido["command"] = "demo"
elif senttext[:1] == ":":
	sentemoji = re.search("\:(.*?)\:", fs.getvalue("text")).group(0)[1:-1:]

	emjfile = ""

	try:
		normem = (item for item in emoji if (item["short_name"] == sentemoji or sentemoji in item["short_names"])).next()
		emjfile = "https://raw.githubusercontent.com/iamcal/emoji-data/master/img-apple-64/" + normem["image"]
	except:
		try:
			emjfile = el[sentemoji]
		except:
			print "Sorry, couldn't find your emoji!"
			sys.exit(0)
	
	emojido["command"] = "image"
	emojido["value"] = emjfile
else:
	print "Hello there. Looks like you're trying to do something with LEDmoji. Here's what you can do:\n/ledmoji [emoji] - display the emoji on the display\n/ledmoji off - turn the display off\n/ledmoji brightness [0..100] - set the brightness level\n/ledmoji text [text] - display some text on the display\n/ledmoji url [url] - download the image at the specified url and display it\n/ledmoji demo - display some interesting built-in animation"
	sys.exit(0)	

from autobahn.twisted.websocket import WebSocketClientProtocol, \
    WebSocketClientFactory

class MyClientProtocol(WebSocketClientProtocol):
    def onOpen(self):
        self.sendMessage(json.dumps(emojido).encode('utf8'))
        self.sendClose()

    def onClose(self, wasClean, code, reason):
	from twisted.internet import reactor
        reactor.callFromThread(reactor.stop)
	print "Command sent!"

from twisted.python import log
from twisted.internet import reactor

factory = WebSocketClientFactory(u"ws://127.0.0.1:9000")
factory.protocol = MyClientProtocol

reactor.connectTCP("127.0.0.1", 9000, factory)
reactor.run()

