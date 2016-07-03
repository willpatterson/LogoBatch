.PHONY: init dev-clean install-clean clean travis-test

init:
	-mkdir .env
	virtualenv .env
	pip install --upgrade pip
	pip install --upgrade setuptools
	python setup.py develop


travis-test:
	python -m unittest discover

clean:
	$(CLEAN)

dev-clean:
	$(CLEAN)
	-rm -rf ImageFudge.egg-info

install-clean:
	$(CLEAN)
	-rm -rf ImageFudge.egg-info
	-rm -rf build
	-rm -rf dist
	-rm -rf .env

$(CLEAN):
	find . -iname "*.pyc" -delete
	find . -iname "*.pyo" -delete
	find . -iname "__pycache__" -delete
