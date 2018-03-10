import sys
import logging
from abc import ABC, abstractmethod


class BaseOutput(ABC):
    def __init__(self, ret):
        """
        Output handler for salt execution return objects

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
    def description(key):
        """
        Extracts a descriptive portion of an execution ID naming pattern.

        Args:
            key (str): The execution ID from which to extract the description

        Returns:
            str: The description of the execution
        """
        return key.split('_|-')[1]

    @abstractmethod
    def ordered_result(self, result):
        """Returns an ordered dictionary of the execution result

        Args:
            result (dict): The execution result dictionary to be ordered

        Returns:
            OrderedDict
        """
        pass
