# -*- coding: utf-8 -*-
"""Base output handler"""
import sys
import logging
from terminaltables import AsciiTable, SingleTable


class BaseOutput(object):
    """Output handler for salt execution return objects"""

    def __init__(self, ret):
        """

        Args:
            ret (dict): The dictionary the is returned as a result of running salt command via REST API.
        """
        self.log = logging.getLogger('{}.{}'.format(self.__module__, type(self).__name__))
        self.raw_data = ret
        self.data = self.ordered_result(ret)
        self.total_ms = {}
        self.colored = True

        if sys.stdout.encoding == 'utf-8':
            self.safe = False
        else:
            self.safe = True

    @staticmethod
    def extract_id(key):
        """
        Extracts a descriptive portion of an execution ID naming pattern.

        Args:
            key (str): The execution ID from which to extract the description

        Returns:
            str: The description of the execution
        """

        try:
            _id = key.split('_|-')[1]
        except IndexError:
            _id = key
        return _id

    def ordered_result(self, result):
        """Returns an ordered dictionary of the execution result

        Args:
            result (dict): The execution result dictionary to be ordered

        Returns:
            OrderedDict
        """
        pass

    @staticmethod
    def format_duration(duration):
        """Formats duration into a more human readable value.

        Args:
            duration (float): Duration time in milliseconds.

        Returns:
            str: The formatted duration.
        """

        seconds = duration / 1000
        if seconds > 60:
            formatted_duration = '{0:1.2f}min'.format(seconds / 60)
        elif seconds >= 1:
            formatted_duration = '{0:1.2f}s'.format(seconds)
        else:
            formatted_duration = '{0:1.2f}ms'.format(duration)

        return formatted_duration

    def _plot_duration(self, duration, total_duration, max_bar_size=30):
        """Returns a bar and the percentage value of the duration in relation to the total.

        Args:
            duration (float): The duration.
            total_duration (float): The total duration (Usually of a highstate).
            max_bar_size (int, optional): Defaults to 30. The bar size that corresponds to 100%.

        Returns:
            tuple: the bar, the percentage value
        """

        ticks = ('█', '▌', '|')
        plot_bar = ''
        percentage = 0

        if self.safe:
            the_tick = ticks[2]
        else:
            the_tick = ticks[0]

        try:
            factor = max_bar_size * duration / total_duration
            plot_bar = str(the_tick * int(factor))
            percentage = factor * 100 / max_bar_size
        except ZeroDivisionError:
            self.log.warning('Unable to format zero duration.')

        return plot_bar, '{0:>5.2f}%'.format(percentage)

    @staticmethod
    def format_time(value, unit):
        """Converts milliseconds to the specified unit.

        Args:
            value (float): The time in milliseconds.
            unit (str): The unit to convert to. `s`: for seconds, `min`: for minutes.

        Returns:
            str: Formatted time
        """

        formatted_value = value

        if unit == 's':
            formatted_value = value / 1000
        elif unit == 'min':
            formatted_value = value / 3600000
        elif unit == 'ms':
            return value
        return '{0:>5.2f}'.format(formatted_value)

    def _create_table(self, data, title=None):
        """Creates a console printable table based on the provided data.

        Args:
            data (list): List of data (As expected by terminaltables's table classes).
            title (str, optional): The table title.

        Returns:
            str: A console printable table.
        """

        if self.safe:
            table = AsciiTable(data)
        else:
            table = SingleTable(data)

        if title:
            table.title = ' {} '.format(title)

        table.inner_column_border = False
        table.inner_footing_row_border = True

        return table.table

    def set_color(self, color_method, items):
        """Sets a terminal color for all items in a list

        Args:
            color_method: A color method from the Color class to be used to format the list items.
            items: A list of items to be colored.
        Returns:
            list
        """
        if self.colored:
            return [color_method(item, auto=True) for item in items]
        return items
