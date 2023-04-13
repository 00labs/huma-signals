.PHONY: lint, lint-check, test, run-local

lint:
	poetry run autoflake --verbose -r .
	poetry run black .
	poetry run flake8 --max-line-length 120 --ignore "E203, W503" .
	poetry run isort .
	poetry run mypy --show-error-codes .
	poetry run pylint huma_signals

lint-check:
	poetry run black --check .
	poetry run flake8 --max-line-length 120 --ignore "E203, W503" .
	poetry run isort --check .
	poetry run mypy --show-error-codes .
	poetry run pylint huma_signals

test:
	ENV=test poetry run python3 -m pytest -v --cov=huma_signals --color=yes --cov-report term-missing --ignore=tests/adapters/request_network

run-local:
	ENV=development poetry run python3 -m uvicorn huma_signals.api.main:app --reload
