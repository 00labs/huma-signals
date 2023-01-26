.PHONY: lint, lint-check, test, run-local

lint:
	poetry run autoflake --in-place --remove-all-unused-imports --verbose -r huma_signals tests
	poetry run black huma_signals tests --target-version py310
	poetry run flake8 huma_signals tests --max-line-length 120 --ignore "E203, W503"
	poetry run isort huma_signals tests -v
	poetry run mypy --show-error-codes .
	poetry run pylint huma_signals

lint-check:
	poetry run black huma_signals tests --target-version py310 --check
	poetry run flake8 huma_signals tests --max-line-length 120 --ignore "E203, W503"
	poetry run isort --check huma_signals tests -v
	poetry run mypy --show-error-codes .
	poetry run pylint huma_signals

test:
	ENV=test poetry run python3 -m pytest -v --cov=huma_signals --color=yes

run-local:
	ENV=development poetry run python3 -m uvicorn huma_signals.api.main:app --reload
