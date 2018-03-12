import logging
import json
from saltypie import Salt
from saltypie.output import OrchestrationOutput

LOG = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)

def main():
    salt = Salt(
        url='https://192.168.70.11:8000',
        username='saltapiuser',
        passwd='abc123',
        trust_host=True
    )
    salt.eauth = 'pam'

    ret = salt.execute(
        client=Salt.CLIENT_RUNNER,
        fun='state.orch',
        args=['orch'],
        pillar={'sleep': 1}
    )
    print(json.dumps(ret, indent=4))


main()