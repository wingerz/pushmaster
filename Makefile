assets=$(shell find www -name '*.js' -or -name '*.css')

head_commit=$(shell git show-ref -s HEAD)

.PHONY: www clean git-version

all: www git-version app.yaml

clean:
	find . -name '*.py[co]' -delete
	rm -f app.yaml
	cd www && make clean

www:
	cd www && make

git-version:
	@echo -n $(head_commit) > .git-version

app.yaml: app-template.yaml git-version
	@echo "generating app.yaml"
	@sed "s/\$$HEAD_COMMIT/$(head_commit)/g" < $< > $@