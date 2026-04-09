"""Fake phone number generation in 020-XXXX-XXXX format"""

import random


def generate_phone(rng: random.Random) -> str:
    """Generate a fake phone number in 020-XXXX-XXXX format."""
    return f"020-{rng.randint(0, 9999):04d}-{rng.randint(0, 9999):04d}"
