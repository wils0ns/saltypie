"""Base output handler"""
import sys
import logging


class BaseOutput(object):
    """Output handler for salt execution return objects"""

    def __init__(self, ret):
        """

        Args:
            ret (dict): The dictionary the is returned as a result of running salt command via REST API.
        """
        self.log = logging.getLogger(__name__)
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
        return key.split('_|-')[1]

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

    def _plot_duration(self, duration, total_duration, max_bar_size=30, safe=None):
        ticks = ('█', '▌', '|')
        plot_bar = ''
        percentage = 0

        if safe is None:
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
        