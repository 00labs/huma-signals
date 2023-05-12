import pathlib

import dotenv

# Fixtures registered below will be made globally available.
pytest_plugins = [
    "tests.fixtures.clients.eth.eth_fixtures",
    "tests.fixtures.clients.polygon.polygon_fixtures",
    "tests.fixtures.clients.request.request_fixtures",
]

dotenv.load_dotenv(dotenv_path=pathlib.Path(__file__).parent / "dotenv" / "test.env")
