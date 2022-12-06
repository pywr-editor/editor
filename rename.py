import os
import re
from pathlib import Path


def snake_case(name):
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def main(path):
    filenames = Path(path).glob("*")

    for filename in filenames:
        print(f"{filename.name} => {snake_case(filename.name)}")
        filename.rename(filename.parent / snake_case(filename.name))
        # os.rename(filename, snake_case(filename))
        # os.remove(filename)


if __name__ == "__main__":
    main("pywr_editor/style")
