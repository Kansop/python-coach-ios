"""The full lesson path, in order: every lessons/uNN_*.py module, sorted by number."""

import importlib
from pathlib import Path


def all_units():
    units = []
    for path in sorted(Path(__file__).parent.glob("u[0-9][0-9]_*.py")):
        module = importlib.import_module(f"{__package__}.{path.stem}")
        units.extend(module.units())
    return units
