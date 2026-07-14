import logging

from config_log import setup_logging
from generator import generate_clicks, generate_products, generate_users

setup_logging()

logger = logging.getLogger(__name__)


def run_pipeline():
    logger.info("--- INICIANDO PIPELINE DE DADOS ---")

    users = generate_users(15)
    products = generate_products(10)
    clicks = generate_clicks(50, products, users)

    logger.info("--- PIPELINE FINALIZADO COM SUCESSO ---")


if __name__ == "__main__":
    run_pipeline()
