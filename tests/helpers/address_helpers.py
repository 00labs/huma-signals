import string

import factory
import faker

fake = faker.Faker()


def fake_hex_address() -> str:
    """
    Generates a fake Ethereum address.
    """
    hex_digits = fake.lexify(text="?" * 40, letters=string.hexdigits + string.digits)
    return f"0x{hex_digits}".lower()


def fake_hex_address_factory() -> factory.LazyFunction:
    """
    Returns a `factory.LazyFunction` that generates a fake Ethereum address.
    """
    return factory.LazyFunction(lambda: fake_hex_address())
