import logging
from functools import wraps
from random import random, uniform
from time import sleep
from typing import Callable

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def select_data(
    invalid_factory: Callable[[], any] | any,
    valid_factory: Callable[[], any] | any,
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
                logging.warning(
                    f"[LATÊNCIA SIMULADA] Gargalo na rede detectado. Atrasando {delay:.2f}s..."
                )
                sleep(delay)
            return func(*args, **kwargs)

        return wrapper

    return decorator
