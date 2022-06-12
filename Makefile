PROJ_DIR := optio
DOXY_DIR := docs/doxygen

.PHONY: all tests docs build release-test release-prod clean

all:
	echo "optio"

tests:
	python3 -m unittest discover tests/

docs:
	mkdir -p $(DOXY_DIR)
	doxygen

build:
	python3 -m build

release-test:
	twine upload --repository testpypi dist/*

release-prod:
	twine upload dist/*

clean:
	rm -rf $(DOXY_DIR) build/ dist/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
