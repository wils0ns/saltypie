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
        fun='test.sleep',
        args=[10],
        wait=True
    )

    print(json.dumps(ret, indent=2))

main()