import logging
from saltypie import Salt

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

    ret = salt.local_async(
        target='*',
        fun='test.arg',
        kwargs={'a': 1, 'b': 2},
        wait=True
    )
    print(ret)

main()
