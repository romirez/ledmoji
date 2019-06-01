#!/usr/bin/env python

import urllib2, urllib, os, sys, commands, json, random
import shlex, subprocess, logging, time
from autobahn.twisted.websocket import WebSocketClientProtocol, WebSocketClientFactory
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.internet import reactor

brightness = 75
imageurl = ""
process = None

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',filename='/var/log/emojiclient.log',level=logging.INFO)
logger = logging.getLogger(__name__)

def update(emojido):
    global imageurl
    global brightness
    global process
    if (emojido["command"] == "off"):
        if (process != None):
            process.kill()
            process = None
        imageurl = ""
    elif (emojido["command"] == "brightness"):
        brightness = int(emojido["value"])
        if (imageurl != ""):
            if (process != None): 
                process.kill()
                process = None
            process = subprocess.Popen(shlex.split("/home/pi/led-image-viewer --led-brightness=" + str(brightness) + " --led-gpio-mapping=adafruit-hat-pwm --led-pwm-lsb-nanoseconds 200 /home/pi/emoji &"))
        return
    elif (emojido["command"] == "text"):
        if (process != None):
            process.kill()
            process = None
        process = subprocess.Popen(shlex.split("python /home/pi/runtext.py -r 32 -m adafruit-hat-pwm -b " + str(brightness) + " -t '" + emojido["value"] + "'"))
        return
    elif (emojido["command"] == "demo"):
        if (process != None):
            process.kill()
            process = None
        
        process = subprocess.Popen(shlex.split("/home/pi/led-image-viewer --led-brightness=" + str(brightness) + " --led-gpio-mapping=adafruit-hat-pwm --led-pwm-lsb-nanoseconds 200 \"/home/pi/demoimg/" + random.choice(os.listdir("/home/pi/demoimg")) + "\" &"))
    elif (emojido["command"] == "image"):
        if (imageurl != emojido["value"]):
            imageurl = emojido["value"]
            img = urllib2.urlopen(emojido["value"])
            with open("/home/pi/emoji", "wb") as output:
                output.write(img.read())

            format = commands.getstatusoutput("identify -format \"%m\" /home/pi/emoji[0]")
            print str(format) + "\n"
    
            if (format[1] == "PNG"):
                os.system("convert /home/pi/emoji -background black -flatten /home/pi/emoji")
            #if (format[1] == "GIF"):
            #    os.system("convert /home/pi/emoji -background black -alpha off /home/pi/emoji")

        if (process != None):
            process.kill()
            process = None

        process = subprocess.Popen(shlex.split("/home/pi/led-image-viewer --led-brightness=" + str(brightness) + " --led-gpio-mapping=adafruit-hat-pwm --led-pwm-lsb-nanoseconds 200 /home/pi/emoji &"))



class MyClientProtocol(WebSocketClientProtocol):
    KEEPALIVE_INTERVAL = 5

    def check_keepalive(self):
        last_interval = time.time() - self.last_ping_time
        if last_interval > 2*self.KEEPALIVE_INTERVAL:
            self.dropConnection(abort=True)
        else:
            self.schedule_keepalive()

    def schedule_keepalive(self):
        self.keepalive_fut = reactor.callLater(self.KEEPALIVE_INTERVAL, self.check_keepalive)

    def onConnect(self, response):
        print("Server connected: {0}".format(response.peer))
        logger.info("Server connected: {0}".format(response.peer))
        self.sendMessage(u"listen vancouver".encode('utf8'))

    def onOpen(self):
        print("WebSocket connection open.")
        logger.info("WebSocket connection open")
        self.last_ping_time = time.time()
        self.schedule_keepalive()

    def onPing(self, payload):
        self.last_ping_time = time.time()
        self.sendPong(payload)

    def onMessage(self, payload, isBinary):
        print("Text message received: {0}".format(payload.decode('utf8')))
        logger.info("Text message received: {0}".format(payload.decode('utf8')))
        try:
            update(json.loads(payload.decode('utf8')))
        except:
            logger.info("Exception in message handling")
            print("Exception in message handling")

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))
        logger.info("WebSocket connection closed: {0}".format(reason))

    def connection_lost(self, exc):
        print("lost")
        self.keepalive_fut.cancel()

class EmojiClientFactory(ReconnectingClientFactory, WebSocketClientFactory):

        protocol = MyClientProtocol

        maxDelay = 20

        def startedConnecting(self, connector):
            print('Started to connect.')
            logger.info('Started to connect.')

        def clientConnectionLost(self, connector, reason):
            print('Lost connection. Reason: {}'.format(reason))
            logger.info('Lost connection. Reason: {}'.format(reason))
            ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

        def clientConnectionFailed(self, connector, reason):
            print('Connection failed. Reason: {}'.format(reason))
            logger.info('Connection failed. Reason: {}'.format(reason))
            ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

if __name__ == '__main__':
    import sys

    from twisted.python import log
    from twisted.internet import reactor

    log.startLogging(sys.stdout)

    emojido = {'command': 'demo'}
    update(emojido)

    factory = EmojiClientFactory(u"ws://romirez.com:9000")
    factory.protocol = MyClientProtocol

    reactor.connectTCP("romirez.com", 9000, factory)
    reactor.run()

