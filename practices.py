"""Practice Python fundamentals with small, reusable functions."""


def greet(name: str) -> str:
    """Return a friendly greeting for a person."""
    return f"Hello, {name}!"


def is_even(number: int) -> bool:
    """Return whether an integer is even."""
    return number % 2 == 0


def count_vowels(text: str) -> int:
    """Count the vowels in text, regardless of letter case."""
    return sum(character in "aeiou" for character in text.lower())


def calculate_total(prices: list[float]) -> float:
    """Return the sum of a list of prices."""
    return sum(prices)
