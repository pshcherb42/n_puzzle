.PHONY: run test clean

run:
	python3 main.py $(ARGS)

test:
	python3 -m pytest -q

clean:
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -name "*.pyc" -delete