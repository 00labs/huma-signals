# Getting started

## Requirements

The Decentralized Signal Portfolio is developed in Python. We use [Poetry](https://python-poetry.org/) to manage dependency for these software packages and [FastAPI](https://fastapi.tiangolo.com/) services.

We suggest you use python version >= 3.10. The development environment is tested using [venv](https://docs.python.org/3/library/venv.html) for python env management.

### Running local server

```bash
make run-local
```

Go to `http://localhost:8000/docs` and you can make requests through the UI.

## Development environment

### Poetry

Poetry is a tool for dependency management and packaging for Python. It creates a lockfile to guarantee reproducible installs and distribution. Highly recommended to browse through [poetry usage](https://python-poetry.org/docs/basic-usage/) if not familiar with it already.

Please install it following the official installer. For macOS users, note brew install may not install poetry correctly.

```bash
curl -sSL https://install.python-poetry.org | python3 -`
```

### Install dependencies

Poetry automatically creates new venv for packages with `pyproject.toml`.
(optional) VS Code users might find setting `poetry config virtualenvs.in-project true` makes it easier to manage the python interpreter.

```bash
poetry install
```

### Code style

To ensure code consistency we have CI to check code style. We use `black`, `flake8`, `isort` and `pylint` with some customization. You can run the CI check with

```bash
make lint-check
```

To automatically fix issues, run

```bash
make lint
```

### Type hints and validation

In this project, we require all code to use type hints in order to ensure the reliability and maintainability of our codebase.

Using [Type Hints](https://peps.python.org/pep-0484/) and [Pydantic](https://pydantic-docs.helpmanual.io/) in our project allows us to improve the quality and reliability of our code. Type hints provide a way to specify the expected data types for function arguments and return values, which can help catch errors at runtime and improve code readability. Pydantic adds additional features on top of type hints, such as automatic data validation and data conversion, which can help prevent errors and ensure that our code is working with consistent, correct data.

We run `mypy` as part of the `lint` command to type check the code.

### Pre-commit hooks

We use [`pre-commit`](https://pre-commit.com/) to run hooks to automatically format and lint code. You can run the following command set it up:

```bash
pre-commit install
```

### Address casing

Addresses from transactions or smart contracts will be normalized to all lowercase internally. This makes it easier to query and aggregate across multiple data sources. Just make sure to `.lower()` API inputs when comparing input addresses.

### Running tests

To run the whole test suite.

```bash
make test
```

To run individual tests:

```bash
ENV=test poetry run python3 -m pytest {Path to the test file}
```

### Pull requests

- Please create pull requests early to start the conversation about the changes.
- The pull request title should summarize the contribution. Prefix with [WIP] if the PR is still a work in progress.
- All new codes should have an extensive suite of tests with necessary fixtures included. All CI tests need to pass before merging.

### Deployment

We use GitHub workflows to manage CI and CD pipelines. Once the new PR is merged, a new docker image will be built and pushed to [container repository](https://aws.amazon.com/ecr/). Currently, the final step in applying Terraform change is managed by Huma DAO.
