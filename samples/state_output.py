import os
import json
import logging

from saltypie.output import StateOutput

logging.basicConfig(level=logging.DEBUG)

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

DATA_FILES = [
    os.path.join(THIS_FOLDER, 'state.json'),
    os.path.join(THIS_FOLDER, 'local_state.json'),
]


def main():
    for data in DATA_FILES:
        with open(data) as ret:
            out = StateOutput(json.load(ret))
            # out.colored = False
            for table in out.tables():
                print(table)


main()
