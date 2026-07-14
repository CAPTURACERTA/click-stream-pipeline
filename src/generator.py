import logging
from datetime import datetime, timedelta, timezone
from random import choice, randint, uniform

from faker import Faker

from .models import Click, Product, User
from .utils import select_data, simulate_latency

fake = Faker()

logger = logging.getLogger(__name__)


@simulate_latency(chance=0.50, min_seconds=0.10, max_seconds=2.0)
def generate_users(num_users: int = 10) -> list[User]:
    users = []
    for _ in range(num_users):
        name = select_data("", lambda: fake.name())

        users.append(User(name=name))

    return users


@simulate_latency(chance=0.50, min_seconds=0.10, max_seconds=2.0)
def generate_products(num_products: int = 10) -> list[Product]:
    products = []
    for _ in range(num_products):
        name = select_data(
            "",
            lambda: (
                f"{fake.color_name()} {fake.bs().title()} {fake.bothify('##??').upper()}"
            ),
        )
        price = select_data(
            lambda: choice(["free", "not-available", None]),
            lambda: round(uniform(10, 100), 2),
        )

        products.append(
            Product(
                name=name,
                price=price,
            )
        )

    return products


@simulate_latency(chance=0.50, min_seconds=0.10, max_seconds=2.0)
def generate_clicks(
    num_clicks: int, products: list[Product], users: list[User]
) -> list[Click]:
    clicks = []
    for _ in range(num_clicks):
        user_id = select_data(None, lambda: choice(users)._id)
        product_id = select_data(None, choice(products)._id)

        clicks.append(
            Click(
                user_id=user_id,
                product_id=product_id,
                timestamp=datetime.now(timezone.utc)
                - timedelta(minutes=randint(0, 60)),
            )
        )

    return clicks
