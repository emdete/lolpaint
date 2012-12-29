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

# Sample Main Programs:
if __name__ == '__main__':
	import pygame
	from pygame.locals import *
	from time import sleep
	from sys import argv

	def test(repeat, port, baudrate):
		lolshield = LolShield(port=port, baudrate=int(baudrate))
		lolshield.update(data='0' * LolShield.width * LolShield.height)
		for n in range(repeat):
			for v in range(2):
				for y in range(LolShield.height):
					for x in range(LolShield.width):
						lolshield.set_pixel(x, y, v)
					sleep(0.3)
			for v in range(2):
				for x in range(LolShield.width):
					for y in range(LolShield.height):
						lolshield.set_pixel(x, y, v)
					sleep(0.3)

	def basic_test(repeat, port, baudrate):
		'''
		As the BasicTest sample from the lolshield library
		'''
		lolshield = LolShield(port=port, baudrate=int(baudrate))
		for n in range(repeat):
			b = [0, ] * (LolShield.width + 1)
			while b.pop(-1) != 0x3fff:
				for x in range(LolShield.width):
					for y in range(LolShield.height):
						lolshield.set_pixel(x, y, bool(b[y] & (1 << x)))
				b.insert(0, (b[0] << 1) | 1)
			while b.pop(-1) != 0:
				b.insert(0, (b[0] << 1) & 0x3fff)
				for x in range(LolShield.width):
					for y in range(LolShield.height):
						lolshield.set_pixel(x, y, bool(b[y] & (1 << x)))
			b = 0
			for m in range(2 * LolShield.width):
				if b >= 0x3fff or b != 0 and b & 1 == 0:
					b = (b << 1) & 0x3fff
				else:
					b = (b << 1) | 1
				for x in range(LolShield.width):
					for y in range(LolShield.height):
						lolshield.set_pixel(x, y, bool(b & (1 << x)))


	def pylolgraph(repeat, port, baudrate):
		'''
		Use pygame to draw to a window & copy the content to the lolshield.
		'''
		scale = 40
		pygame.init()
		# screenSurf Setup
		screenSurf = pygame.display.set_mode(LolShield.calc_multiple(scale))
		pygame.display.set_caption('pylolgraph')
		clock = pygame.time.Clock()
		lolshield = LolShield(port=port, baudrate=int(baudrate))
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
		lolshield.update(data='0' * LolShield.width * LolShield.height)

	def animate_gif(repeat, port, baudrate):
		'''
		Read an gif image & copy it to the lolshield.
		'''
		lolshield = LolShield(port=port, baudrate=int(baudrate))
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
