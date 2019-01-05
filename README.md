# Saltypie - salt-api wrapper and state return parser.



## Installation

```bash
   pip install saltypie
```

## Local client example

Code:

```python
from saltypie import Salt
from saltypie.output import StateOutput


salt = Salt(
    url='https://192.168.70.11:8000',
    username='saltapiuser',
    passwd='abc123',
    trust_host=True
)

ret = salt.execute(
    client=Salt.CLIENT_LOCAL,
    target='*',
    fun='state.apply',
    pillar={'sleep': 1}
)

sout = StateOutput(ret)
print(sout)
```

Output:

```
+ minion01 ---------------------------------------------------------+
| State                         Plot          %       ms     Result |
+-------------------------------------------------------------------+
| test succeed with changes     ||||||||||||  42.13%  0.404  True   |
| test succeed without changes  ||||||||      29.61%  0.284  True   |
| test no operation             ||||||||      28.26%  0.271  True   |
+-------------------------------------------------------------------+
| Total elapsed time: 0.96ms                                        |
+-------------------------------------------------------------------+
```

## Runner client example

Code:

```python
from saltypie import Salt
from saltypie.output import OrchestrationOutput

salt = Salt(
    url='https://192.168.70.10:8000',
    username='saltapiuser',
    passwd='abc123',
    trust_host=True
)
salt.eauth = 'pam'

ret = salt.execute(
    client=Salt.CLIENT_RUNNER,
    fun='state.orch',
    args=['orch_fail'],
    pillar={'sleep': 1}
)

orchout = OrchestrationOutput(ret, salt)
print(orchout.summary_table(max_bar_size=100, time_unit='s'))
```

Output:

```
   + Orchestration -----------------------------------------------------------------+
   | Step                        Plot                       %       Time(s)  Result |
   +--------------------------------------------------------------------------------+
   | Step01                      |||||||||||||||||||||||||  25.20%   5.13    True   |
   | Step02                      ||||||||||||||||||||||||   24.69%   5.03    True   |
   | Step03                      ||||||||||||||||||||||||   24.79%   5.05    True   |
   | Step04                      |||||||||||||||||||||||||  25.32%   5.16    False  |
   +--------------------------------------------------------------------------------+
   | Total elapsed time: 20.37s                                                     |
   +--------------------------------------------------------------------------------+
```

## Terminal safe mode

All output classes have the `safe` property that is set to `False` if the terminal encoding is dectected to be *utf-8*. To always use safe mode set it to `True`:

Example:

```python
from saltypie import Salt
from saltypie.output import StateOutput, OrchestrationOutput

sout = StateOutput(ret)
sout.safe = True
# play with the tables here ...

orchout = OrchestrationOutput(ret, salt)
orchout.safe = True
# play with the tables here ...
```

## Disable table coloring
Set the output object `colored` property to `False`:

Example:
```python
from saltypie import Salt
from saltypie.output import OrchestrationOutput

orchout = OrchestrationOutput(ret, salt)
orchout.colored = False
# play with the tables here ...
```

More examples
=============

https://gitlab.com/cathaldallan/saltypie/tree/master/examples


Documentation
=============

https://cathaldallan.gitlab.io/saltypie/