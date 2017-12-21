#!/usr/bin/env python2
# -*- coding: utf-8 -*-
'''
demo.py

this is the demo of the serpaint library

authors:

	Eric Pavey - www.akeric.com - 2010-08-03 (the pygame idea, the serial idea)
	http://www.cibomahto.com/2010/08/programming-the-lol-shield-using-animated-gifs/ (the gif read idea)
	M. Dietrich - pyneo.org - 2011-01-02 (the integration of all; the new, stateless protocol)

licence:

	free to use, enjoy.

warenty:

	none, will probably grill your equipment, kill little babies or your granma

'''
__version__ = '1.0'

#from serpaint import SerialShield
from pygamedemo import PyGameShield as SerialShield
from time import sleep
from sys import argv

# Sample Main Programs:
def test(repeat, port, baudrate):
	lolshield = SerialShield(port=port, baudrate=int(baudrate))
	lolshield.clear()
	for n in range(repeat):
		for v in range(2):
			for y in range(SerialShield.height):
				for x in range(SerialShield.width):
					lolshield.set_pixel(x, y, v)
				sleep(0.3)
		for v in range(2):
			for x in range(SerialShield.width):
				for y in range(SerialShield.height):
					lolshield.set_pixel(x, y, v)
				sleep(0.3)

def basic_test(repeat, port, baudrate):
	'''
	As the BasicTest sample from the lolshield library
	'''
	lolshield = SerialShield(port=port, baudrate=int(baudrate))
	for n in range(repeat):
		b = [0, ] * (SerialShield.width + 1)
		while b.pop(-1) != 0x3fff:
			for x in range(SerialShield.width):
				for y in range(SerialShield.height):
					lolshield.set_pixel(x, y, bool(b[y] & (1 << x)))
			b.insert(0, (b[0] << 1) | 1)
		while b.pop(-1) != 0:
			b.insert(0, (b[0] << 1) & 0x3fff)
			for x in range(SerialShield.width):
				for y in range(SerialShield.height):
					lolshield.set_pixel(x, y, bool(b[y] & (1 << x)))
		b = 0
		for m in range(2 * SerialShield.width):
			if b >= 0x3fff or b != 0 and b & 1 == 0:
				b = (b << 1) & 0x3fff
			else:
				b = (b << 1) | 1
			for x in range(SerialShield.width):
				for y in range(SerialShield.height):
					lolshield.set_pixel(x, y, bool(b & (1 << x)))

def animate_gif(repeat, port, baudrate):
	'''
	Read an gif image & copy it to the lolshield.
	'''
	lolshield = SerialShield(port=port, baudrate=int(baudrate))
	for n in range(repeat):
		# get it from http://www.cibomahto.com/wp-content/uploads/2010/08/ripple.gif
		lolshield.play(filename='ripple.gif', wait=0.3)


def main(port='/dev/ttyUSB0', baudrate=19200, repeat=3, *args):
	'''
	run all three samples.
	'''
	animate_gif(repeat, port, baudrate, *args)
	test(repeat, port, baudrate, *args)
	basic_test(repeat, port, baudrate, *args) # this single one

if __name__ == '__main__':
	exit(main(*argv[1:]))
# vim:tw=0:nowrap
