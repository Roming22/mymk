from time import sleep

from mymk.utils.logger import logger


def main(string: str) -> None:
    while True:
        logger.info(end=string)
        sleep(2)


if __name__ == "__main__":
    main(".")
