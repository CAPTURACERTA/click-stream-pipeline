from datetime import datetime, timedelta, timezone
from random import choice, randint, uniform

from faker import Faker

from .models import Click, Product, User

fake = Faker()


def generate_users(num_users: int = 10) -> list[User]:
    users = []
    for _ in range(num_users):
        user = User(name=fake.name())
        users.append(user)
    return users


def generate_products(num_products: int = 10) -> list[Product]:
    products = []
    for _ in range(num_products):
        product = Product(
            name=f"{fake.color_name()} {fake.bs().title()} {fake.bothify('##??').upper()}",
            price=round(uniform(10, 100), 2),
        )
        products.append(product)
    return products


def generate_clicks(
    num_clicks: int, products: list[Product], users: list[User]
) -> list[Click]:
    clicks = []
    for _ in range(num_clicks):
        click = Click(
            user_id=choice(users)._id,
            product_id=choice(products)._id,
            timestamp=datetime.now(timezone.utc) - timedelta(minutes=randint(0, 60)),
        )
        clicks.append(click)
    return clicks
