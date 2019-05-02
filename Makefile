export PYTHONPATH := proweather:$(PYTHONPATH)

GLOBAL_PYTHON := python3.7
PYTHON := .venv/bin/python
PYTEST := .venv/bin/pytest

ifndef DATES
    DATES := $(shell date +%Y-%m-%d)
endif

.PHONY: all clean-cache clean-data clean-venv prepare run

all: | clean-cache clean-data clean-venv prepare run

clean-cache:
	@find proweather -name "__pycache__" -type d -exec rm -rf {} +

clean-data:
	@rm -rf data

clean-venv:
	@rm -rf .venv

prepare:
	@$(GLOBAL_PYTHON) -m venv .venv
	@$(PYTHON) -m pip install --upgrade pip
	@$(PYTHON) -m pip install -r requirements.txt

run:
	@$(PYTHON) -m proweather.main $(DATES)
