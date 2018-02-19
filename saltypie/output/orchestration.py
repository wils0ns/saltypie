#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .state import StateOutput


class OrchestrationOutput(StateOutput):
    def __init__(self, ret):
        super(OrchestrationOutput, self).__init__(ret)

    def ordered_result(self, result):
        ordered = {}

        self.log.debug('Ordering orchestration output...')
        for master in result[0]['data']:
            pass

