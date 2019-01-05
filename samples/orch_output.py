import os
import json
from saltypie.output import OrchestrationOutput

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

DATA_FILES = [
    os.path.join(THIS_FOLDER, 'orch.json'),
    os.path.join(THIS_FOLDER, 'failed_orch.json'),
]

def main():
    for data in DATA_FILES:
        with open(data) as ret:
            out = OrchestrationOutput(json.load(ret))
            # out.colored = False
            print(out.summary_table())

main()
