# Getting started

## Requirements

The Decentralized Signal Portfolio is developed in Python. We use [Poetry](https://python-poetry.org/) for dependency management.

The current required Python version is 3.10.

## Development environment

### Poetry

Poetry is a tool for dependency management and packaging for Python. It creates a lockfile to guarantee reproducible installs and distribution. Please browse through [poetry usage](https://python-poetry.org/docs/basic-usage/) if you are not familiar with it yet.

Please install it using the official installer. For macOS users, `brew install` may not install poetry correctly.

```bash
curl -sSL https://install.python-poetry.org | python3 -`
```

### Install dependencies

Poetry automatically creates new venv for packages with `pyproject.toml`.
(optional) VS Code users might find it useful to set `poetry config virtualenvs.in-project true`. This makes it easier to manage the Python interpreter.

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

In this project, all code are fully typed in order to ensure the reliability and maintainability of our codebase.

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

To run the whole test suite:

```bash
make test
```

To run a single test:

```bash
poetry run python3 -m pytest <test_file.py[::describe_test_func[::it_does_abc]]>
```

You may need to set specific environment variables in order to run tests for some of the adapters. The required
env vars can be found in the respective directory of the adapter. You can either provide the value of the env vars
by adding a file called `test.env` under the [`dotenv` directory](../tests/dotenv) (we have provided a file called
`example.env` for your reference), or specify them directly as part of the command that runs the tests.

### Pull requests

- Please create pull requests early to start the conversation about the changes.
- The pull request title should summarize the contribution. Prefix with [WIP] if the PR is still a work in progress.
- All new code should have an extensive suite of tests with necessary fixtures included. All CI tests need to pass before merging.

### Package publishing

New changes will be published to [PyPI](https://pypi.org/project/huma-signals/) by Huma as they become available.
