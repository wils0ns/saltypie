import json
from saltypie.output import OrchestrationOutput

def main():
    with open('samples/orch.json') as ret:
        orchout = OrchestrationOutput(json.load(ret))

main()
