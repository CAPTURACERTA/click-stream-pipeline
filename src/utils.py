from random import random
from typing import Callable


def select_data(
    invalid_factory: Callable[[], any] | any,
    valid_factory: Callable[[], any] | any,
    probability_of_invalid: float = 0.5,
):
    if random() < probability_of_invalid:
        return invalid_factory() if callable(invalid_factory) else invalid_factory

    return valid_factory() if callable(valid_factory) else valid_factory
