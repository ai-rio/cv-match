"""Simple clean test file that should pass all type checks."""


def simple_function(name: str) -> str:
    """Simple function with proper type annotations."""
    return f"Hello, {name}!"


def another_function(x: int, y: int) -> int:
    """Another simple function."""
    return x + y


# This should pass all type checking
result = simple_function("World")
total = another_function(5, 3)

# Use the variables to avoid unused variable warnings
print(f"Result: {result}")
print(f"Total: {total}")
