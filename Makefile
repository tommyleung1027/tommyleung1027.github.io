.PHONY: update-papers serve test

ifneq ("$(wildcard .gem/bin/bundle)","")
BUNDLE_CMD=GEM_HOME="$(PWD)/.gem" GEM_PATH="$(PWD)/.gem" PATH="$(PWD)/.gem/bin:$(PATH)" .gem/bin/bundle
else
BUNDLE_CMD=bundle
endif

update-papers:
	python3 scripts/build_paper_index.py

serve:
	$(BUNDLE_CMD) exec jekyll serve

test:
	python3 -m py_compile scripts/build_paper_index.py
	python3 scripts/build_paper_index.py
	$(BUNDLE_CMD) exec jekyll build
