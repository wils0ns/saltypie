import os
import json
from saltypie.output import OrchestrationOutput

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

ORCH_FILES = [
    os.path.join(THIS_FOLDER, 'orch.json'),
    os.path.join(THIS_FOLDER, 'failed_orch.json'),
]

def main():
    for orch_file in ORCH_FILES:
        with open(orch_file) as ret:
            orchout = OrchestrationOutput(json.load(ret))
            # orchout.colored = False
            print(orchout.summary_table())

main()
