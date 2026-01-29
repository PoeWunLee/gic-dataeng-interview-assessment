import logging

def init_logger()->None:
    """Utility to set configs for logging format"""
    logging.basicConfig(
        level=logging.INFO,
        format="| %(levelname)s | %(asctime)s | %(message)s ",
        datefmt="%Y-%m-%d %H:%M:%S"
    )