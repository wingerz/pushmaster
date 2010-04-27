assets=$(shell find www -name '*.js' -or -name '*.css')

.PHONY: www clean

all: www

clean:
	find . -name '*.py[co]' -delete
	cd www && make clean

www:
	cd www && make


