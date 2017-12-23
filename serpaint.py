#!/usr/bin/env python2
# -*- coding: utf-8 -*-
'''
serpaint.py

this is a py library to paint on the lolshield from a pc via usb. there must be
a receiver installed on the arduino (see below for source). the main idea of
this implementation is to have all needed information for the receiver in one
byte. it contains state of the led and also the position that should be
updated. compared to the previous implementation by eric this doesn't need more
traffic for complete updates but reduces the the traffic if only diffs of the
image are updated.

authors:

	Eric Pavey - www.akeric.com - 2010-08-03 (the pygame idea, the serial idea)
	http://www.cibomahto.com/2010/08/programming-the-lol-shield-using-animated-gifs/ (the gif read idea)
	M. Dietrich - pyneo.org - 2011-01-02 (the integration of all; the new, stateless protocol)

licence:

	free to use, enjoy.

warenty:

	none, will probably grill your equipment, kill little babies or your granma

for use with serpaint.pde arduino sketch (source below).

it was tested with an arduino like one from:

	http://www.arduino.cc/

and a lolshield like one from:

	http://jimmieprodgers.com/kits/lolshield/

it uses pygame to display a local version of the lolshield display from:

	http://www.pygame.org

and sends data via pyserial from:

	http://pypi.python.org/pypi/pyserial

there are three main usage of the object:

	- paint a copy of the pygame surface on the lolshield

	- give set_pixel to paint single leds on or off

	- read a gif and display it live on the lolshield

see example usages at the end.

the pde is as simple as this:

---
#include <Charliplexing.h>

void setup() {
	LedSign::Init();
	Serial.begin(19200);
	}

void loop () {
	while (Serial.available() >= 1) {
		unsigned char received = Serial.read();
		int val = received % 2;
		received /= 2;
		byte x = received % 14;
		received /= 14;
		byte y = received % 9;
		received /= 9;
		LedSign::Set(x,y,val);
		}
	}
---
'''
__version__ = '1.0'

from serial import Serial
from time import sleep

class SerialShield(Serial):
	'''
	The LolSheild object is a subclass of the Serial object since it piggybacks
	off of that functionality to transfer paint operations to the lolshield.
	'''
	width = 14 # Width of lolshield
	height = 9 # Height of lolshield

	def __init__(self, port, baudrate, **kwargs):
		'''
		Init the Serial superclass, and setup some default doublebuffer data.
		'''
		super(SerialShield, self).__init__(port=port, baudrate=baudrate, **kwargs)
		self.rtscts = False
		self.xonxoff = False
		self.timeout = 1
		self.writeTimeout = 1
		#self.open()
		self.doublebuffer = [0, ] * self.height

	def clear(self, v=0):
		for x in range(self.width):
			for y in range(self.height):
				self.set_pixel(x, y, v)

	def set_pixel(self, x, y, v=1):
		#'''
		#Set pixel on lolshield to on or off.
		#'''
		v = 1 if v else 0
		v1 = 1 if self.doublebuffer[y] & (1 << x) else 0
		if v1 != v:
			# we have no performance problem so this is more illustrative:
			b = 0
			b *= SerialShield.height
			b += y
			b *= SerialShield.width
			b += x
			b *= 2
			b += v
			self.write(chr(b))
			self.doublebuffer[y] ^= (1 << x)

	def set_record(self):
		' start recording (work in progress) '
		self.write(chr(253))

	def set_stop(self):
		' stop recording (work in progress) '
		self.write(chr(254))

	def set_replay(self):
		' replay recording (work in progress) '
		self.write(chr(255))

	def mplayer(self, filename='dvd://1'):
		' play a video on the lolshield (work in progress) '
		command = ' | '.join((
			r"mplayer {i} -vf scale={w}:{h} -ss {s} -frames {f} -vo pnm -ao null -quiet".format(
				i=filename,
				w=SerialShield.width,
				h=SerialShield.height,
				s=0,
				f=500,
				),
			r"grep ^VIDEO",
			r"sed 's/^.*\ \([0-9]*\.[0-9]*\)\ fps.*$/\1/'", ))

	def play(self, filename='ripple.gif', wait=0.3):
		'''
		Copy gif image to lolshield.
		'''
		from PIL.Image import open as image_open
		def ImageSequence(im):
			ix = 0
			try:
				while True:
					if ix:
						im.seek(ix)
					yield im
					ix += 1
			except EOFError:
				return # end of sequence
		# Open image
		im = image_open(filename)
		# For each frame in the image, convert it to black & white, then into the
		# LoLShield format
		BIT = 2 << SerialShield.width
		for frame in ImageSequence(im):
			# Convert to black and white
			frame = frame.convert("1")
			buffr = frame.tobytes()
			# For each row in the image
			for row in range(SerialShield.height):
				line = (ord(buffr[row*2]) << 8) + ord(buffr[row*2 + 1])
				for col in range(SerialShield.width):
					self.set_pixel(col, row, bool(line & (BIT >> col)))
			if wait:
				sleep(wait)

def main(port='/dev/ttyUSB0', baudrate=19200, repeat=3, *args):
	from time import sleep
	from random import shuffle
	lolshield = SerialShield(port=port, baudrate=int(baudrate))
	s = list([(n,m) for n in range(lolshield.width) for m in range(lolshield.height)])
	while True:
		shuffle(s)
		for x,y in s:
			lolshield.set_pixel(x, y, 0)
		sleep(.5)
		shuffle(s)
		for x,y in s:
			lolshield.set_pixel(x, y, 1)
		sleep(.5)

if __name__ == '__main__':
	from sys import argv
	exit(main(*argv[1:]))
# vim:tw=0:nowrap
