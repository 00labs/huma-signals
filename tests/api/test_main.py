from huma_signals.api import main


def describe_get_health() -> None:
    async def it_returns_ok() -> None:
        response = await main.get_health()
        assert response == "ok"
