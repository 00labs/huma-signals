import asyncio
import string

import faker
import structlog

from huma_signals.adapters.banking import plaid_client
from huma_signals.settings import settings

fake = faker.Faker()

logger = structlog.get_logger(__name__)


async def generate() -> None:
    client = plaid_client.PlaidClient(
        plaid_env=settings.plaid_env,
        plaid_client_id=settings.plaid_client_id,
        plaid_secret=settings.plaid_secret,
    )
    wallet_address = fake.lexify(
        text=f"0x{'?' * 40}", letters="abcdefABCDEF" + string.digits
    )
    user_token = await client.create_user_token(wallet_address=wallet_address)
    token = await client.create_sandbox_public_token(
        institution_id="ins_109508",
        user_token=user_token,
    )
    logger.info(f"Wallet address: {wallet_address}. Public token: {token}")


if __name__ == "__main__":
    asyncio.run(generate())
