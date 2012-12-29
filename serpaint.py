#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
lolpaint.py

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
from pygame.transform import smoothscale
import sys, os, Image


class LolShield(Serial):
	'''
	The LolSheild object is a subclass of the Serial object since it piggybacks
	off of that functionality to transfer paint operations to the lolshield.
	'''
	width = 14 # Width of lolshield
	height = 9 # Height of lolshield

	def __init__(self, port, baudrate, **kwargs):
		'''
		Init the Serial superclass, and setup some default surface data.
		'''
		super(LolShield, self).__init__(port=port, baudrate=baudrate, **kwargs)
		self.rtscts = False
		self.xonxoff = False
		self.timeout = 1
		self.writeTimeout = 1
		self.open()
		# Premade surface the size of the lolshield, that will ultimately have
		# its data sampled and sent to the lolshield:
		self.surface = None
		self.lol_surface = None
		self.double = [0, ] * self.height

	@classmethod
	def calc_multiple(clazz, multiple):
		'''
		Calculate a window size that is a multiple of the size of a lolshield.
		'''
		return map(lambda n: n * multiple, (LolShield.width, LolShield.height, ))

	def set_surface(self, surface):
		'''
		Set the surface that will have it's pixels sent to the lolshield.
		It needs to be the same aspect ratio as the lolshield, but can be a multiple
		of the resolution.
		'''
		self.surface = surface
		surfWidth, surfHeight = self.surface.get_size()
		# Make sure surface width and height are a power of the lolshield
		# width & height:
		if surfWidth % LolShield.width:
			raise Exception('Passed in surface width must be multiple of %s, currently is: %s'% LolShield.width,surfWidth)
		if surfHeight % LolShield.height:
			raise Exception('Passed in surface width must be multiple of %s, currently is: %s'% LolShield.height,surfHeight)
		# Make sure that the surface aspect ratio is the same as the lolshield:
		if surfWidth / LolShield.width != surfHeight / LolShield.height:
			raise Exception('Surface aspect ratio must match that of lolshield: %sx%s. Is currently %sx%s'% (
				LolShield.width,
				LolShield.height,
				surfWidth,
				surfHeight,
				))
		self.lol_surface = pygame.Surface((LolShield.width, LolShield.height))

	def set_pixel(self, x, y, v=1):
		#'''
		#Set pixel on lolshield to on or off.
		#'''
		#v = 1 if v else 0
		#v1 = 1 if self.double[y] & (1 << x) else 0
		#if v1 != v:
			# we have no performance problem so this is more illustrative:
			b = 0
			b *= LolShield.height
			b += y
			b *= LolShield.width
			b += x
			b *= 2
			b += v
			self.write(chr(b))
			self.double[y] ^= (1 << x)

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
				w=LolShield.width,
				h=LolShield.height,
				s=0,
				f=500,
				),
			r"grep ^VIDEO",
			r"sed 's/^.*\ \([0-9]*\.[0-9]*\)\ fps.*$/\1/'", ))

	def play(self, filename='ripple.gif', wait=0.3):
		'''
		Copy gif image to lolshield.
		'''
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
		im = Image.open(filename)
		# For each frame in the image, convert it to black & white, then into the
		# LoLShield format
		BIT = 2 << LolShield.width
		for frame in ImageSequence(im):
			# Convert to black and white
			frame = frame.convert("1")
			buffr = frame.tostring()
			# For each row in the image
			for row in range(LolShield.height):
				line = (ord(buffr[row*2]) << 8) + ord(buffr[row*2 + 1])
				for col in range(LolShield.width):
					self.set_pixel(col, row, bool(line & (BIT >> col)))
			if wait:
				sleep(wait)

	def update(self, data=None):
		'''
		Update the data to be sent to the Arduino/lolshield.
		Should be executed every loop.

		data : str | list : Optional: By default will use self.surface, but instead
			can bypass it and send in direct data if any is provided. Furthermore,
			there is built in test data: If the string 'test' is passed in, it
			will light up the whole lolshield. Otherwise accepts either a string with
			126 characters, or a list with 126 single entries. Must be 0 or 1 int
			/ string values ineither case.
		'''
		# Send the data to the Arduino/lolshield if it is ready to accept it.
		# If directly passed in data, use it:
		if data:
			if data == 'test':
				# Set all self.data values to 1 by default, to light up the
				# whole lolshield, for testing.
				for x in range(LolShield.width):
					for y in range(LolShield.height):
						self.set_pixel(x, y)
			else:
				# If data is a list, convert it to a string:
				for x in range(LolShield.width):
					for y in range(LolShield.height):
						self.set_pixel(x, y, data[y * LolShield.width + x] == '1')
		# otherwise process self.surface:
		else:
			# First, shrink it to match res of lolshield:
			smoothscale(self.surface, (LolShield.width, LolShield.height), self.lol_surface)
			# Now extract value data to send:
			for x in range(LolShield.width):
				for y in range(LolShield.height):
					h, s, v, a, = self.lol_surface.get_at((x, y, ))
					self.set_pixel(x, y, v >= 50)

