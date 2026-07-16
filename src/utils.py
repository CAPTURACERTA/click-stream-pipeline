import asyncio
import logging
from functools import wraps
from inspect import iscoroutinefunction
from random import random, uniform
from time import sleep
from typing import Any, Callable

logger = logging.getLogger(__name__)


def select_data(
    invalid_factory: Callable[[], Any] | Any,
    valid_factory: Callable[[], Any] | Any,
    probability_of_invalid: float = 0.05,
):
    if random() < probability_of_invalid:
        return invalid_factory() if callable(invalid_factory) else invalid_factory

    return valid_factory() if callable(valid_factory) else valid_factory


def simulate_latency(
    chance: float = 0.10, min_seconds: float = 0.1, max_seconds: float = 1.5
):
    """Optionally simulate network latency for synchronous or asynchronous calls.

    Async functions use ``asyncio.sleep`` so the event loop can keep serving
    other messages while a simulated request is delayed.
    """
    if not 0 <= chance <= 1:
        raise ValueError("chance must be between 0 and 1.")
    if min_seconds < 0 or max_seconds < min_seconds:
        raise ValueError("Latency bounds must be non-negative and ordered.")

    def decorator(func):
        if iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                if random() < chance:
                    delay = uniform(min_seconds, max_seconds)
                    logger.warning(
                        "[SIMULATED LATENCY] Network bottleneck detected. Delaying by %.2fs...",
                        delay,
                    )
                    await asyncio.sleep(delay)
                return await func(*args, **kwargs)

            return async_wrapper

        @wraps(func)
        def wrapper(*args, **kwargs):
            if random() < chance:
                delay = uniform(min_seconds, max_seconds)
                logger.warning(
                    "[SIMULATED LATENCY] Network bottleneck detected. Delaying by %.2fs...",
                    delay,
                )
                sleep(delay)
            return func(*args, **kwargs)

        return wrapper

    return decorator
