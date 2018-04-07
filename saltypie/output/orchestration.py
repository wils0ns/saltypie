#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Salt orchestration output parser"""

import json
from collections import OrderedDict
from colorclass import Color, Windows
from terminaltables import AsciiTable, SingleTable

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
        self.parsed_data = self.parse_data()

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

    def summary_table(self, max_bar_size=30, time_unit='s'):
        """Returns a table listing the orchestration steps and information about its duration and result.

        Args:
            max_bar_size (int, optional): Defaults to 30. Size of the bar plot equivalent to 100%
                of the execution time.
            time_unit (str, optional): Defaults to 's'. Step duration unit.
                ms: milliseconds, s: seconds or min: minutes.

        Returns:
            str: A console printable table representation of the orchestration.
        """

        table_data = [['Step', 'Plot', '%', 'Time({})'.format(time_unit), 'Result']]

        for _, orch in self.parsed_data.items():
            for step in orch['data']:
                for step_name, step_data in step.items():
                    plot_bar, percentage = self._plot_duration(
                        duration=step_data['duration'],
                        total_duration=orch['total_duration'],
                        max_bar_size=max_bar_size
                    )

                    _id = self.extract_id(step_name)
                    duration = self.format_time(step_data['duration'], unit=time_unit)

                    line = (_id, plot_bar, percentage, duration, step_data['result'])
                    if step_data['result']:
                        table_data.append([Color.cyan(item, auto=True) for item in line])
                    else:
                        table_data.append([Color.red(item, auto=True) for item in line])

            table_data.append([
                'Total elapsed time: {}'.format(
                    self.format_duration(orch['total_duration'])
                )
            ])

        return self._create_table(data=table_data, title='Orchestration')

    def detailed_table(self):
        pass
    
