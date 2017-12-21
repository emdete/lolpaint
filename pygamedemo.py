#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from serpaint import SerialShield
from pygame.transform import smoothscale
import pygame
from pygame.locals import *
from sys import argv

# use an pygame window to visualize the lolshield
class PyGameShield(SerialShield):
	def __init__(self, port, baudrate, scale=40, **kwargs):
		super(PyGameShield, self).__init__(port=port, baudrate=baudrate, **kwargs)
		pygame.init()
		self.scale = scale
		self.surface = pygame.display.set_mode((SerialShield.width * scale, SerialShield.height * scale, ))
		pygame.display.set_caption('pylolgraph')
		self.lol_surface = pygame.Surface((SerialShield.width, SerialShield.height))

	def update(self):
		# First, shrink it to match res of lolshield:
		smoothscale(self.surface, (SerialShield.width, SerialShield.height), self.lol_surface)
		# clear screen (to paint leds)
		self.surface.fill(Color('black'))
		# extract value data to send:
		for x in range(SerialShield.width):
			for y in range(SerialShield.height):
				h, s, v, a, = self.lol_surface.get_at((x, y, ))
				self.set_pixel(x, y, v >= 50)

	def set_pixel(self, x, y, v):
		super(PyGameShield, self).set_pixel(x, y, v)
		# paint led
		if v:
			pygame.draw.circle(self.surface, Color('yellow'), (self.scale*x+self.scale/2, self.scale*y+self.scale/2), self.scale/2)
		else:
			pygame.draw.circle(self.surface, Color('black'), (self.scale*x+self.scale/2, self.scale*y+self.scale/2), self.scale/2)
		# update our pygame display:
		pygame.display.update()

	def demo(self):
		looping = True
		# Main loop
		clock = pygame.time.Clock()
		while looping:
			self.surface.fill(Color('black'))
			# detect for events
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					looping = False
					self.clear()
				elif event.type == MOUSEBUTTONDOWN and event.button == 1: # MOUSEBUTTONUP MOUSEMOTION
					# when the LMB is pressed move donut position
					mx, my = event.pos
					# Make a nice donut on screen
					pygame.draw.circle(self.surface, Color('white'), (mx, my), self.scale * 4)
					pygame.draw.circle(self.surface, Color('black'), (mx, my), self.scale * 2)
					# Update the pixels to be sent to the lolshield, and send them:
					self.update()
			# Maintain our framerate:
			clock.tick(20)

def main(port='/dev/ttyUSB0', baudrate=19200, repeat=3, *args):
	'''
	Use pygame to draw to a window & copy the content to the lolshield.
	'''
	lolshield = PyGameShield(port=port, baudrate=int(baudrate), scale=60)
	lolshield.demo()

if __name__ == '__main__':
	exit(main(*argv[1:]))
# vim:tw=0:nowrap
