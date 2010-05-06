assets=$(shell find www -name '*.js' -or -name '*.css')

.PHONY: www clean deploy

all: www

clean:
	find . -name '*.py[co]' -delete
	rm -f app.yaml
	cd www && make clean

www:
	cd www && make

deploy:
	appcfg.py update -V $(shell bash app-version.sh) .

run:
	dev_appserver.py .
