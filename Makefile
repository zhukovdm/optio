PROJ_DIR := optio
DOXY_DIR := docs/doxygen

.PHONY: tests docs clean

tests:
	python3 -m unittest discover tests/

docs:
	mkdir -p $(DOXY_DIR)
	doxygen

clean:
	rm -rf $(DOXY_DIR) build/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
