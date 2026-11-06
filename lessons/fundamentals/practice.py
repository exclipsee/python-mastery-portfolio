"""Small examples for the first Python fundamentals lesson."""


def greet(name: str) -> str:
    """Return a short greeting for the person named."""
    return f"Hello, {name}!"


def is_even(number: int) -> bool:
    """Return True when number is divisible by two."""
    return number % 2 == 0


def count_vowels(text: str) -> int:
    """Count the vowels in text, without considering letter case."""
    vowels = "aeiou"
    count = 0

    for character in text.lower():
        if character in vowels:
            count += 1

    return count


def calculate_total(prices: list[float]) -> float:
    """Add the prices in a list and return their total."""
    total = 0.0

    for price in prices:
        total += price

    return total


