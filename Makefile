PROJ_DIR := optio
DOXY_DIR := docs/doxygen

.PHONY: all tests docs clean

all:
	echo "optio"

tests:
	python3 -m unittest discover tests/

docs:
	mkdir -p $(DOXY_DIR)
	doxygen

clean:
	rm -rf $(DOXY_DIR) build/ dist/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
