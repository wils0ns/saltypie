from saltypie import Salt

salt = Salt('https://163.185.10.104:8000', username='drillops-cm', passwd='removeme')

ret = salt.execute(
    client=Salt.CLIENT_LOCAL,
    target='*local-cm',
    fun='coda_node.start_commission',
    # options: node_id, ip or role
    args=['', '', 'containers-pc'],
    # kwargs={'role': 'containers-pc'}
)

print(ret['return'])