"""Dirty data generator -- intentional noise for data cleaning exercises.

Applies ~5-10% noise to selected tables when --dirty-data flag is used.
Types of noise: leading/trailing spaces, mixed case, inconsistent formats,
NULL vs empty string, etc.
"""

from __future__ import annotations

import random
from typing import Any


def apply_dirty_data(data: dict[str, list[dict]], seed: int = 42, noise_rate: float = 0.05) -> dict[str, list[dict]]:
    """Apply realistic noise to generated data for cleaning exercises.

    Returns modified data dict (in-place mutation).
    """
    rng = random.Random(seed + 999)

    # Customer name noise: leading/trailing spaces, extra spaces
    _apply_noise(data.get("customers", []), "name", rng, noise_rate, [
        lambda v, r: f"  {v}",              # leading spaces
        lambda v, r: f"{v}  ",              # trailing spaces
        lambda v, r: f"  {v}  ",            # both
        lambda v, r: v.replace(" ", "  "),   # double spaces
    ])

    # Customer email noise: mixed case
    _apply_noise(data.get("customers", []), "email", rng, noise_rate * 0.5, [
        lambda v, r: v.upper(),
        lambda v, r: v[0].upper() + v[1:],
        lambda v, r: v.replace("@", " @"),   # space before @
    ])

    # Customer phone noise: inconsistent format
    _apply_noise(data.get("customers", []), "phone", rng, noise_rate, [
        lambda v, r: v.replace("-", ""),      # no hyphens
        lambda v, r: v.replace("-", " "),     # spaces instead of hyphens
        lambda v, r: f"+82-{v[1:]}",         # international format mixed in
    ])

    # Customer birth_date: some empty strings instead of NULL
    for row in data.get("customers", []):
        if row.get("birth_date") is None and rng.random() < noise_rate:
            row["birth_date"] = rng.choice(["", "N/A", "unknown"])

    # Customer gender: inconsistent values
    _apply_noise(data.get("customers", []), "gender", rng, noise_rate, [
        lambda v, r: v.lower() if v else v,   # 'm' instead of 'M'
        lambda v, r: "Male" if v == "M" else ("Female" if v == "F" else v),
        lambda v, r: "" if v is None else v,   # empty string instead of NULL
    ])

    # Product name noise: unicode issues, extra whitespace
    _apply_noise(data.get("products", []), "name", rng, noise_rate * 0.3, [
        lambda v, r: f" {v}",
        lambda v, r: v.replace(" ", "\u00a0"),  # non-breaking space
    ])

    # Order notes: some with only whitespace
    for row in data.get("orders", []):
        if row.get("notes") is None and rng.random() < noise_rate * 0.5:
            row["notes"] = rng.choice(["", " ", "  ", "N/A", "-"])

    # Review content: some have HTML entities or extra newlines
    _apply_noise(data.get("reviews", []), "content", rng, noise_rate * 0.3, [
        lambda v, r: f"{v}\n" if v else v,
        lambda v, r: v.replace(".", ".\n") if v else v,
    ])

    return data


def _apply_noise(
    rows: list[dict],
    field: str,
    rng: random.Random,
    rate: float,
    transforms: list,
):
    """Apply random transforms to a field in a fraction of rows."""
    for row in rows:
        if rng.random() < rate and row.get(field) is not None:
            transform = rng.choice(transforms)
            try:
                row[field] = transform(row[field], rng)
            except (TypeError, AttributeError):
                pass  # skip if transform fails on this value
