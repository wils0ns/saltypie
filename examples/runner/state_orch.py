import logging
import json
from saltypie import Salt
from saltypie.output import OrchestrationOutput

LOG = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)


def main():
    salt = Salt(
        url='https://localhost:8000',
        username='admin',
        passwd='admin',
        trust_host=True
    )
    salt.eauth = 'pam'

    ret = salt.runner_async(
        fun='state.orch',
        args=['orch_fail'],
        pillar={'sleep': 1},
        wait=True
    )

    # print(json.dumps(ret, indent=2))

    orchout = OrchestrationOutput(ret, salt)
    # orchout.safe = False
    print(orchout.summary_table(max_bar_size=100, time_unit='s', show_minions=True))
    for sout in orchout.get_state_outputs():
        print('Step:', sout['step'])
        print('---')
        for table in sout['data'].tables(time_unit='s'):
            print(table)

    # print(json.dumps(orchout.data, indent=2))
    # print(orchout.get_step_names())
    # print(json.dumps(orchout.parse_data(dict_only=True), indent=4))

main()
