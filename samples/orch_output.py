import os
import json
import logging

from saltypie.output import OrchestrationOutput

logging.basicConfig(level=logging.DEBUG)

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

DATA_FILES = [
    os.path.join(THIS_FOLDER, 'orch.json'),
    os.path.join(THIS_FOLDER, 'failed_orch.json'),
    os.path.join(THIS_FOLDER, 'async_failed_orch.json'),
]


def main():
    for data in DATA_FILES:
        with open(data) as ret:
            print('\n\n', '#'*10, data.upper(), '#'*10)
            orchout = OrchestrationOutput(json.load(ret))
            # out.colored = False
            print(orchout.summary_table(max_bar_size=100, time_unit='s', show_minions=True))

            print('Failed orch steps: ', orchout.failed_steps)

            for sout in orchout.get_state_outputs():
                print('\n### Step:', sout['step'])
                print('---')
                for table in sout['data'].tables(time_unit='s'):
                    print(table)


main()
