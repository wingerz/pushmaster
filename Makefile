assets=$(shell find www -name '*.js' -or -name '*.css')

head_commit=$(shell bash head-commit.sh)

.PHONY: www clean git-version

all: www git-version app.yaml

clean:
	find . -name '*.py[co]' -delete
	rm -f app.yaml
	cd www && make clean

www:
	cd www && make

git-version:
	@echo $(head_commit) > .git-version

app.yaml: app-template.yaml git-version
	@echo "generating app.yaml"
	@sed "s/\$$HEAD_COMMIT/$(head_commit)/g" < $< > $@