import logging


def setup_logging() -> None:
    root_logger = logging.getLogger()

    root_logger.setLevel(logging.INFO)

    if not root_logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        file_handler = logging.FileHandler("pipeline.log", mode="a", encoding="utf-8")
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
