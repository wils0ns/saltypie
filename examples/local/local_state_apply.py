import logging, json, os
from saltypie import Salt
from saltypie.output import StateOutput

LOG = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)

SAMPLES_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        '../../samples'
    )
)

def main():
    with open(os.path.join(SAMPLES_DIR, 'local_state.json')) as _file:
        data = json.load(_file)
    
    sout = StateOutput(data)
    print(sout)
main()