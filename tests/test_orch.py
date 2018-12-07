import logging
import json
from saltypie import Salt
from saltypie.output import OrchestrationOutput

LOG = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)


def main():

    with open('samples/failed_orch.json') as _file:
        ret = json.load(_file)

    orchout = OrchestrationOutput(ret)
    # orchout.safe = False
    print(orchout.summary_table(max_bar_size=100, time_unit='s', show_minions=True))

    print('Failed orch steps: ', orchout.failed_steps)

    for sout in orchout.get_state_outputs():
        print('Step:', sout['step'])
        print('---')
        for table in sout['data'].tables(time_unit='s'):
            print(table)

    

    # print(json.dumps(orchout.data, indent=2))
    # print(json.dumps(orchout.parse_data(dict_only=True), indent=4))

main()
