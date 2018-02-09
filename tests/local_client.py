from saltypie import Salt
import logging

LOG = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)

salt = Salt()
salt.eauth = 'ldap'
ret = salt.execute(
    client=Salt.CLIENT_LOCAL,
    target='*local-cm',
    fun='test.ping',
    # options: node_id, ip or role
    # args=['', '', 'containers-pc'],
    # kwargs={'role': 'containers-pc'}
)

print(ret['return'])