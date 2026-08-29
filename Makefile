.PHONY: all setup test build run backend frontend clean

PYTHON ?= python
NPM ?= npm

all: setup test build

setup:
	$(PYTHON) -m pip install -r backend/requirements.txt
	cd frontend && $(NPM) install

seed:
	PYTHONPATH=backend $(PYTHON) data/seeds/seed_data.py

test:
	$(PYTHON) -m pytest backend/tests -v

build:
	cd frontend && $(NPM) run build

backend:
	$(PYTHON) -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000 --reload

frontend:
	cd frontend && $(NPM) run dev

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	rm -rf frontend/.next
