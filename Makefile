.PHONY: lint, lint-check, test, run-local

lint:
	poetry run autoflake  --in-place --remove-all-unused-imports --verbose -r huma_signals tests
	poetry run black huma_signals tests --target-version py38 -l120
	poetry run flake8 huma_signals tests --max-line-length 120 --ignore "E203, W503" 
	poetry run isort huma_signals tests

lint-check:
	poetry run black huma_signals tests --target-version py38 -l120 --check 
	poetry run flake8 huma_signals tests --max-line-length 120 --ignore "E203, W503"
	poetry run isort --check huma_signals tests 

test:
	ENV=test poetry run python3 -m pytest -v --color=yes

run-local:
	ENV=development poetry run python3 -m uvicorn huma_signals.api.main:app --reload
