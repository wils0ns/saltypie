#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import colorama
import logging
from collections import OrderedDict
from colorclass import Color, Windows
from terminaltables import AsciiTable, SingleTable

from saltypie.output import BaseOutput


class OrchestrationOutput(BaseOutput):
    """Output handler for salt orchestration return objects"""

    def ordered_result(self, result):
        ordered = {}

        self.log.debug('Ordering orchestration output...')
        for master in result[0]['data']:
            pass
