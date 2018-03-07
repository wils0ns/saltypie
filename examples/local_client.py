from pprint import pprint
from saltypie import Salt
from saltypie.output import StateOutput
import logging

LOG = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)

salt = Salt(
    url='https://192.168.70.10:8000',
    username='saltapiuser',
    passwd='abc123',
    trust_host=True
)
salt.eauth = 'pam'

# TODO check proper syntax for kwargs with local client
# ret = salt.execute(
#     client=Salt.CLIENT_LOCAL,
#     target='*',
#     fun='cmod.public',
#     kwargs={'a': 1, 'b': 2}
# )
# print(ret)

ret = salt.execute(
    client=Salt.CLIENT_LOCAL,
    target='*',
    fun='state.apply',
    # args=['test.sleep'],
    # pillar={'sleep': 1}
)
# print(ret)
sout = StateOutput(ret)
print(sout)

# ret = salt.execute(
#     client=Salt.CLIENT_RUNNER,    
#     fun='state.orch',
#     args=['orch'],
#     pillar={'sleep': 1}
# )

# pprint(ret['return'])