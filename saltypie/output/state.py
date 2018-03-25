#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Salt state output parser"""

import sys
import json
from collections import OrderedDict
import colorama
from colorclass import Color, Windows
from terminaltables import AsciiTable, SingleTable

from saltypie.output.base import BaseOutput

colorama.init()

try:
    if sys.stdout.encoding == 'utf-8':
        Windows.enable(auto_colors=True, reset_atexit=True)
except AttributeError:
    pass


class StateOutput(BaseOutput):
    """Output handler for salt state return objects"""

    def ordered_result(self, result):
        """Order states by run number

        Args:
            result (dict): The return object of a `state.apply` execution

        Returns:
            OrderedDict
        """
        ordered = {}

        self.log.debug('Ordering state runs...')
        for minions in result['return']:
            for minion_id in minions:
                states = minions[minion_id]
                try:
                    ordered[minion_id] = OrderedDict(
                        sorted(states.items(), key=lambda k: k[1]['__run_num__']))
                except Exception as exc:
                    self.log.error('Error: Unable to sort state results for %s minion', minion_id)
                    self.log.error('%s: %s', type(exc), exc)
                    self.log.error('State results: \n%s', json.dumps(result, indent=2))
                    exit(1)

        return ordered

    def summary(self, max_chars=None):
        """Returns a summary of a state run with more meaningful data.
        
        ID: the state name extracted from the state key
        Duration: If a state did not run, its duration is set to zero
        Result: `True` or `False` for whether or not the state run successfully
        Changes: `True` or `False` for whether or not the state has made changes to the minion

        Args:
            max_chars (int): Maximum number of characters to display for state ID.
                             If the ID is greater then `max_chars` ellipsis(...) will be added.
        Returns:
            dict
        """
        ret = {}
        for minion_id in self.data:
            ret[minion_id] = {
                'states': [],
                'total_duration': 0,
                'failed_states': [],
                'raw_states': []
            }

            for state_key, state_data in self.data[minion_id].items():

                ret[minion_id]['total_duration'] += state_data.get('duration', 0)

                state_name = BaseOutput.extract_id(state_key)
                if max_chars:
                    max_chars = abs(max_chars)
                    if len(state_name) > max_chars:
                        state_name = state_name[:max_chars] + '...'

                filtered_data = {
                    'id': state_name,
                    'duration': state_data.get('duration', 0),
                    'result': state_data['result'],
                    'changes': state_data['changes'] != {}
                }
                ret[minion_id]['raw_states'].append(state_data)
                ret[minion_id]['states'].append(filtered_data)

                if not state_data['result']:
                    ret[minion_id]['failed_states'].append(filtered_data)

        return ret

    def tables(self, failed_only=False, max_chars=None, safe=None):
        """Creates a list of tables representing the state run for which minion.

        Args:
            failed_only (bool): Whether or not the tables should only contain the failed states
            max_chars (int): Maximum number of characters to display for state ID.
                             If the ID is greater then `max_chars` ellipsis(...) will be added.
            safe (bool): If safe is set to `True`, the table will be created using features that are compatible with
                         most terminals.

        Returns:
            list
        """

        if failed_only:
            states = 'failed_states'
        else:
            states = 'states'

        data = self.summary(max_chars=max_chars)

        if safe is None:
            safe = self.safe

        tables = []
        for minion_id in data:

            if not data[minion_id][states]:
                self.log.debug('No state results found. Skipping `%s`', minion_id)
                continue

            table_data = [['State', 'Time(ms)', 'Result']]

            for state in data[minion_id][states]:
                line = (state['id'], state['duration'], state['result'])
                if state['result']:
                    table_data.append([Color.cyan(item, auto=True) for item in line])
                else:
                    table_data.append([Color.red(item, auto=True) for item in line])

            total_sec = data[minion_id]['total_duration'] / 1000
            if total_sec > 60:
                total_time = '{0:1.2f}min'.format(total_sec / 60)
            else:
                total_time = '{0:1.2f}s'.format(total_sec)
            table_data.append(['Total elapsed time: {}'.format(total_time)])

            if safe:
                table = AsciiTable(table_data)
            else:
                table = SingleTable(table_data)

            table.inner_footing_row_border = True
            table.inner_column_border = False
            table.title = ' {} '.format(minion_id)
            tables.append(table.table)
        return tables

    def graphs(self, failed_only=False, max_chars=None, max_bar_size=30, safe=None):
        """Creates a list of tables representing the state run including a more graphical
        representation of the duration.

        Args:
            failed_only (bool): Whether or not the tables should only contain the failed states
            max_chars (int): Maximum number of characters to display for state ID.
                             If the ID is greater then `max_chars` ellipsis(...) will be added.
            max_bar_size (int): Size of the bar plot equivalent to 100% of the execution time.
            safe (bool): If safe is set to `True`, the table will be created using features that are compatible with
                         most terminals.

        Returns:
            list
        """

        if safe is None:
            safe = self.safe

        ticks = ('█', '▌', '|')

        if failed_only:
            states = 'failed_states'
        else:
            states = 'states'

        data = self.summary(max_chars=max_chars)
        tables = []
        if safe:
            the_tick = ticks[2]
        else:
            the_tick = ticks[0]

        for minion_id in data:

            if not data[minion_id][states]:
                self.log.debug('No state results found. Skipping `%s`', minion_id)
                continue

            table_data = [['State', 'Plot', '%', 'ms', 'Result']]
            for state in data[minion_id][states]:
                try:
                    factor = max_bar_size * state['duration'] / data[minion_id]['total_duration']
                    plot_bar = str(the_tick * int(factor))
                    percentage = factor * 100 / max_bar_size
                except ZeroDivisionError:
                    self.log.warning('Salt execution might have returned with error:\n %s', minion_id)
                    plot_bar = ''
                    percentage = 0

                line = (
                    state['id'],
                    plot_bar,
                    '{0:>5.2f}%'.format(percentage),
                    state['duration'],
                    state['result']
                )

                if self.colored:
                    if state['result']:
                        table_data.append([Color.cyan(item, auto=True) for item in line])
                    else:
                        table_data.append([Color.red(item, auto=True) for item in line])
                else:
                    table_data.append([item for item in line])

            total_sec = data[minion_id]['total_duration'] / 1000
            if total_sec > 60:
                total_time = '{0:1.2f}min'.format(total_sec / 60)
            else:
                total_time = '{0:1.2f}s'.format(total_sec)
            table_data.append(['Total elapsed time: {}'.format(total_time)])

            if safe:
                table = AsciiTable(table_data)
            else:
                table = SingleTable(table_data)

            table.title = ' {} '.format(minion_id)
            table.inner_column_border = False
            table.inner_footing_row_border = True
            tables.append(table.table)

        return tables

    def __str__(self):
        ret = ''
        for graph in self.graphs():
            ret += graph + '\n\n'
        return ret
