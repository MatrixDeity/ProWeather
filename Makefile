GLOBAL_PYTHON=python3.7
PYTHON=./.venv/bin/python
PYTEST=./.venv/bin/pytest

.PHONY: all clean-cache prepare run

all: run

clean-cache:
	@find proweather -name "__pycache__" -type d -exec rm -rf {} +

prepare:
	@$(GLOBAL_PYTHON) -m venv .venv
	@$(PYTHON) -m pip install --upgrade pip
	@$(PYTHON) -m pip install -r requirements.txt

run:
	@$(PYTHON) -m proweather.main
