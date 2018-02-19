from saltypie import Salt
from saltypie.output import StateOutput
import logging

LOG = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)

salt = Salt(url='https://192.168.70.11:8000', username='saltapiuser', passwd='abc123')
salt.eauth = 'pam'
ret = salt.execute(
    client=Salt.CLIENT_LOCAL,
    target='*',
    fun='test.ping',    
)

print(ret['return'])