.PHONY: init dev-clean install-clean clean test

init:
	-mkdir .env
	virtualenv .env
	pip install --upgrade pip
	pip install --upgrade setuptools
	pip install -r requirements.txt
	python setup.py develop

test:
	coverage run -m unittest discover

clean:
	$(CLEAN)

dev-clean:
	$(CLEAN)
	-rm -rf logobatch.egg-info

install-clean:
	$(CLEAN)
	-rm -rf logobatch.egg-info
	-rm -rf build
	-rm -rf dist
	-rm -rf .env

$(CLEAN):
	find . -iname "*.pyc" -delete
	find . -iname "*.pyo" -delete
	find . -iname "__pycache__" -delete
