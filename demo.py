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

from serpaint import LolShield

class PyGameShield(LolShield):
	def __init__(self, port, baudrate, **kwargs):
		super(PyGameShield, self).__init__(port=port, baudrate=baudrate, **kwargs)
		# Premade surface the size of the lolshield, that will ultimately have
		# its data sampled and sent to the lolshield:
		self.surface = None
		self.lol_surface = None

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

# Sample Main Programs:
if __name__ == '__main__':
	import pygame
	from pygame.locals import *
	from time import sleep
	from sys import argv

	def test(repeat, port, baudrate):
		lolshield = PyGameShield(port=port, baudrate=int(baudrate))
		lolshield.update(data='0' * PyGameShield.width * PyGameShield.height)
		for n in range(repeat):
			for v in range(2):
				for y in range(PyGameShield.height):
					for x in range(PyGameShield.width):
						lolshield.set_pixel(x, y, v)
					sleep(0.3)
			for v in range(2):
				for x in range(PyGameShield.width):
					for y in range(PyGameShield.height):
						lolshield.set_pixel(x, y, v)
					sleep(0.3)

	def basic_test(repeat, port, baudrate):
		'''
		As the BasicTest sample from the lolshield library
		'''
		lolshield = PyGameShield(port=port, baudrate=int(baudrate))
		for n in range(repeat):
			b = [0, ] * (PyGameShield.width + 1)
			while b.pop(-1) != 0x3fff:
				for x in range(PyGameShield.width):
					for y in range(PyGameShield.height):
						lolshield.set_pixel(x, y, bool(b[y] & (1 << x)))
				b.insert(0, (b[0] << 1) | 1)
			while b.pop(-1) != 0:
				b.insert(0, (b[0] << 1) & 0x3fff)
				for x in range(PyGameShield.width):
					for y in range(PyGameShield.height):
						lolshield.set_pixel(x, y, bool(b[y] & (1 << x)))
			b = 0
			for m in range(2 * PyGameShield.width):
				if b >= 0x3fff or b != 0 and b & 1 == 0:
					b = (b << 1) & 0x3fff
				else:
					b = (b << 1) | 1
				for x in range(PyGameShield.width):
					for y in range(PyGameShield.height):
						lolshield.set_pixel(x, y, bool(b & (1 << x)))


	def pylolgraph(repeat, port, baudrate):
		'''
		Use pygame to draw to a window & copy the content to the lolshield.
		'''
		scale = 40
		pygame.init()
		# screenSurf Setup
		screenSurf = pygame.display.set_mode(PyGameShield.calc_multiple(scale))
		pygame.display.set_caption('pylolgraph')
		clock = pygame.time.Clock()
		lolshield = PyGameShield(port=port, baudrate=int(baudrate))
		lolshield.set_surface(screenSurf)
		mx, my = 0, 0
		looping = True
		# Main loop
		while looping:
			screenSurf.fill(Color('black'))
			# detect for events
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					looping = False
				elif event.type == MOUSEBUTTONDOWN and event.button == 1: # MOUSEBUTTONUP MOUSEMOTION
					# when the LMB is pressed move donut position
					mx, my = event.pos
			# Make a nice donut on screen
			pygame.draw.circle(screenSurf, Color('white'), (mx, my), scale * 4)
			pygame.draw.circle(screenSurf, Color('black'), (mx, my), scale * 2)
			# Update the pixels to be sent to the lolshield, and send them:
			lolshield.update()
			# update our display:
			pygame.display.update()
			# Maintain our framerate:
			clock.tick(20)
		lolshield.update(data='test')
		sleep(0.3)
		lolshield.update(data='0' * PyGameShield.width * PyGameShield.height)

	def animate_gif(repeat, port, baudrate):
		'''
		Read an gif image & copy it to the lolshield.
		'''
		lolshield = PyGameShield(port=port, baudrate=int(baudrate))
		for n in range(repeat):
			# get it from http://www.cibomahto.com/wp-content/uploads/2010/08/ripple.gif
			lolshield.play(filename='ripple.gif', wait=0.3)

	def main(repeat=3, port='/dev/ttyUSB0', baudrate=19200, *args):
		'''
		run all three samples.
		'''
		#test(repeat, port, baudrate, *args)
		basic_test(repeat, port, baudrate, *args) # this single one
		#animate_gif(repeat, port, baudrate, *args)
		#pylolgraph(repeat, port, baudrate, *args)

	# Execution from shell/icon:
	exit(main(*argv[1:]))
# vim:tw=0:nowrap
