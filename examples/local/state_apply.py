import logging
from saltypie import Salt
from saltypie.output import StateOutput

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
        client=Salt.CLIENT_LOCAL,
        target='*',
        fun='state.apply',
        args=['test.sleep'],
        pillar={'sleep': 1}
    )
    print(ret)
    sout = StateOutput(ret)
    print(sout)

    ret = salt.execute(
        client=Salt.CLIENT_LOCAL,
        target='*',
        fun='state.apply',
        args=['test.sleep'],
        pillar={'sleep': 3},
        async_wait=True
    )
    print(ret)
    sout = StateOutput(ret)
    print(sout)

main()
