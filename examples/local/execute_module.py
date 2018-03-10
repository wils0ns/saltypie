import logging
from saltypie import Salt

LOG = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)

def main():
    salt = Salt(
        url='https://192.168.70.10:8000',
        username='saltapiuser',
        passwd='abc123',
        trust_host=True
    )
    salt.eauth = 'pam'

    ret = salt.execute(
        client=Salt.CLIENT_LOCAL,
        target='local-cm',
        fun='test.arg',
        kwargs={'a': 1, 'b': 2}
    )
    print(ret)

main()
