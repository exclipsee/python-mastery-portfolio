def square(number: int) -> int:
    """Return the square of a number."""
    return number * number


def is_palindrome(text: str) -> bool:
    """Check whether a string is a palindrome ignoring case and spaces."""
    cleaned = "".join(char.lower() for char in text if char.isalnum())
    return cleaned == cleaned[::-1]