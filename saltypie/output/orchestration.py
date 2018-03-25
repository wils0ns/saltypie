#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Salt orchestration output parser"""

import json
from collections import OrderedDict
from colorclass import Color, Windows
from terminaltables import AsciiTable, SingleTable

from saltypie.salt import Salt
from saltypie.output import BaseOutput, StateOutput


class OrchestrationOutput(BaseOutput):
    """Output handler for salt orchestration return objects

    Args:
        ret (dict): The return object of a `state.orch` execution.
        salt (Salt): saltypie's Salt object for connecting to the master where the orchestration
            was executed from. A bug on salt's orcherstration return object prevents it from been
            parsed as a full qualified JSON object when one of its state execution steps fails
    """

    def __init__(self, ret, salt=None):
        super(OrchestrationOutput, self).__init__(ret)
        self.salt = salt

    def ordered_result(self, result):
        """Order orchestration steps by run number.

        Args:
            result (dict): The return object of a `state.orch` execution.

        Returns:
            OrderedDict
        """
        ordered = {}

        self.log.debug('Ordering orchestration output...')
        try:
            for master, _orch in result['return'][0]['data'].items():
                ordered[master] = OrderedDict(
                    sorted(_orch.items(), key=lambda k: k[1]['__run_num__']))
        except Exception as exc:
            self.log.error('Error: Unable to sort orchestration results')
            self.log.error('%s: %s', type(exc), exc)
            self.log.error('Orchestration results: \n%s', json.dumps(result, indent=2))
            exit(1)

        return ordered

    def normalize_state(self, state_data):
        """Normalizes an orchestration state return data by making the `changes` attribute
        consistent even and it fails.

        When normalizing data for failed states, the return object will be retrieved by querying the server
        using the job ID.

        If `OrchestrationOutput.salt` object is not provided, the state data will not be altered.

        Args:
            state_data (dict): State execution dictionary.

        Returns:
            dict: Normalized data
        """

        if state_data['changes']:
            state_data['changes'] = {
                'return': [state_data['changes']['ret']]
            }
        else:
            if self.salt:
                state_return = self.salt.lookup_job(state_data['__jid__'])
                state_data['changes'] = state_return
            else:
                self.log.error(
                    'Error: Unable to fetch data from failed state: `%s`. Salt object not provided.',
                    self.extract_id(state_data.get('__id__'))
                )

        return state_data

    def parse_data(self, dict_only=False):
        """Parses the orchestration data.

        Args:
            dict_only (bool, optional): Defaults to False. State `changes` will be replaced by saltypie.StateOutput
                objects. If this argument is set to true, it will be just an `OrderedDict` instead.

        Returns:
            dict
        """

        ret = dict()
        for master, _orch in self.data.items():
            ret[master] = {
                'data': [],
                'total_duration': 0,
            }

            for key, data in _orch.items():
                ret[master]['total_duration'] += data.get('duration', 0)
                if self.is_salt_state(key):
                    data = self.normalize_state(data)
                    state_output = StateOutput(data['changes'])
                    if dict_only:
                        data['changes'] = state_output.data
                    else:
                        data['changes'] = state_output

                ret[master]['data'].append({key: data})
        return ret

    @staticmethod
    def get_step_type(key):
        """Returns the orcherstration step type based on its key.

        Args:
            key ([str): An orchestration step key.

        Returns:
            str: The orchestration step type.
        """

        return key.split('_|-')[-1]

    @staticmethod
    def is_salt_function(key):
        """Checks whether or not an orchestration step is a salt function execution.

        Args:
            key (str): An orchestration step key.

        Returns:
            bool
        """
        return OrchestrationOutput.get_step_type(key) == 'function'

    @staticmethod
    def is_salt_state(key):
        """Checks whether or not an orcherstration step is a salt state execution.

        Args:
            key (str): An orchestration step key

        Returns:
            bool
        """
        return OrchestrationOutput.get_step_type(key) == 'state'
