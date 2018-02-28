#!/usr/bin/env python2
from socket import socket, AF_INET, SOCK_STREAM
from serpaint import SerialShield

lolshield = SerialShield(port='/dev/ttyUSB0', baudrate=19200, )
sock = socket(AF_INET, SOCK_STREAM)
sock.bind(('0.0.0.0', 1234))
while True:
	sock.listen(0)
	sc, x = sock.accept()
	print('connection from {}:{}'.format(*x))
	l = sc.recv(2000)
	while l:
		i = l.find('\n')
		if i >= 0:
			m = l[:i]
			l = l[i+1:]
			try:
				cmd, x, y, c = m.strip().split()
				x, y = int(x), int(y)
				lolshield.set_pixel(x, y, c == 'ffffff')
			except:
				raise
		l = l + sc.recv(2000)
	sc.close()
