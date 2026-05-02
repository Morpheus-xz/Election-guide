.PHONY: test test-verbose test-coverage lint install run

install:
	pip install -r requirements.txt

run:
	uvicorn app.main:app --reload --port 8080

test:
	GEMINI_API_KEY=test-key pytest tests/ -v --tb=short

test-verbose:
	GEMINI_API_KEY=test-key pytest tests/ -v --tb=long -s

test-coverage:
	GEMINI_API_KEY=test-key pytest tests/ -v --cov=app \
		--cov-report=term-missing --cov-report=html

lint:
	python -m py_compile app/main.py app/config.py app/prompt.py app/__init__.py
	echo "✅ No syntax errors"
