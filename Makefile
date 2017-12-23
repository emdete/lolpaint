#!/usr/bin/env make -f
.PHONY: all dbg run clean

all:

run:
	./serpaint.py
	#./pygamedemo.py
	#./demo.py

dbg:

clean:
	rm -f *.pyc *.pyo


