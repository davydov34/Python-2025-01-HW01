import argparse
import sys

from src.app.log_analyzer import run_analyze
from src.app.logger import logger_init


def getParams():
    """
    Функция получения параметров запуска
    :return:
    """
    params = argparse.ArgumentParser()
    params.add_argument("-c", "--config")

    return params


if __name__ == "__main__":
    args = getParams()
    arg_values = args.parse_args(sys.argv[1:])

    if arg_values.config is None:
        arg_values.config = "config.cfg"

    logger_init()
    run_analyze(arg_values.config)
