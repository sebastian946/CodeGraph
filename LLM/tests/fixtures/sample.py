import os
import sys
from pathlib import Path


def greet(name: str) -> str:
    """Return a personalised greeting."""
    return f"Hello, {name}!"


def process(data: list, verbose: bool = False) -> dict:
    """Process a list of items and return a result dict."""
    result = greet("world")
    return {"processed": result, "count": len(data)}


class Calculator:
    """Simple calculator with basic arithmetic."""

    def add(self, a: int, b: int) -> int:
        """Return the sum of a and b."""
        return a + b

    def subtract(self, a: int, b: int) -> int:
        return a - b

    def compute(self, x: int) -> int:
        """Compute by delegating to add."""
        return self.add(x, 1)
