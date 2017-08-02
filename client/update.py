#!/usr/bin/env python

import urllib2, urllib, os, sys, commands
data = urllib2.urlopen("http://romirez.com/emoji.txt").read()
print data

if data == "":
	os.system("killall led-image-viewer")
	sys.exit(0)

with open("/home/pi/cache.txt", "r") as input:
	cache = input.read()

if (cache == data):
	sys.exit(0)

with open("/home/pi/cache.txt", "wb") as output:
	output.write(data)

img = urllib2.urlopen(data)
with open("/home/pi/emoji", "wb") as output:
	output.write(img.read())

format = commands.getstatusoutput("identify -format \"%m\" /home/pi/emoji[0]")
print str(format) + "\n"

if (format[1] == "PNG"):
	os.system("convert /home/pi/emoji -background black -flatten /home/pi/emoji")
if (format[1] == "GIF"):
	os.system("convert /home/pi/emoji -background black -alpha off /home/pi/emoji")
	print "lol"

os.system("killall led-image-viewer")
os.system("/home/pi/led-image-viewer --led-brightness=75 --led-gpio-mapping=adafruit-hat-pwm /home/pi/emoji &")
