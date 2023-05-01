import string

import factory
import faker

fake = faker.Faker()


def fake_hex_address(length: int = 40) -> str:
    """
    Generates a fake Ethereum address.
    """
    hex_digits = fake.lexify(
        text="?" * length, letters=string.hexdigits + string.digits
    )
    return f"0x{hex_digits}".lower()


def fake_hex_address_factory(length: int = 40) -> factory.LazyFunction:
    """
    Returns a `factory.LazyFunction` that generates a fake Ethereum address.
    """
    return factory.LazyFunction(lambda: fake_hex_address(length))
