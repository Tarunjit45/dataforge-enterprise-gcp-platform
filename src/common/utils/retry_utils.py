"""Retry decorator utility with exponential backoff scaffolding."""

import time
from functools import wraps
from typing import Any, Callable, Type


def retry_on_exception(
    max_retries: int = 3,
    backoff_factor: float = 2.0,
    allowed_exceptions: tuple[Type[Exception], ...] = (Exception,),
) -> Callable:
    """Decorator signature: Retry function on failure with exponential backoff.

    Args:
        max_retries: Maximum attempt count.
        backoff_factor: Multiplicative factor for delay.
        allowed_exceptions: Tuple of exceptions to intercept.

    Returns:
        Callable: Wrapped function.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            delay = 1.0
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except allowed_exceptions as e:
                    if attempt == max_retries:
                        raise e
                    time.sleep(delay)
                    delay *= backoff_factor

        return wrapper

    return decorator
