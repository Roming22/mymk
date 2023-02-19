from time import sleep


def main(string: str) -> None:
    while True:
        print(end=string)
        sleep(2)
