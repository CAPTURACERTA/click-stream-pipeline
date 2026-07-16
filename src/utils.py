import logging
from functools import wraps
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
    def decorator(func):
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
