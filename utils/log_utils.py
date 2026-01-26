import logging

def init_logger()->None:
    logging.basicConfig(
        level=logging.INFO,
        format="| %(levelname)s | %(asctime)s | %(message)s ",
        datefmt="%Y-%m-%d %H:%M:%S"
    )