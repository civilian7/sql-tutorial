"""020-XXXX-XXXX 형식의 가상 전화번호 생성"""

import random


def generate_phone(rng: random.Random) -> str:
    """020-XXXX-XXXX 형식의 가상 전화번호를 생성한다."""
    return f"020-{rng.randint(0, 9999):04d}-{rng.randint(0, 9999):04d}"
