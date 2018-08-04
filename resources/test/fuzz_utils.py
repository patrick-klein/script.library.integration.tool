#!/usr/bin/python
# -*- coding: utf-8 -*-
''' Defines class for fuzzing utils module '''

import string
import random
import unittest

import resources.lib.utils as utils


class UtilsTest(unittest.TestCase):
    ''' Class that contains test cases for fuzzing utils module '''

    def test_clean_name(self):
        ''' runs randomly generated strings through utils.clean_name '''
        keywords = [x[0] for x in utils.MAPPED_STRINGS]
        num_keywords = len(keywords)
        for _ in range(100):
            name_length = random.randint(1, 128)
            test_name = ''
            while len(test_name) < name_length:
                if random.random() < 1. / num_keywords:
                    test_name += random.choice(keywords)
                else:
                    test_name += random.choice(string.printable)
            utils.clean_name(test_name)
