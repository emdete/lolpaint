#!/usr/bin/env make -f
.PHONY: all dbg run clean

all:

run:
	./demo.py
	#./pygamedemo.py

dbg:

clean:
	rm -f *.pyc *.pyo


