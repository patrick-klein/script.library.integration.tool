#!/usr/bin/python
# -*- coding: utf-8 -*-

'''Defines class for fuzzing utils module'''


import string
import random
import unittest

from resources.lib.manipulator import clean_name
from resources.lib.manipulator import MAPPED_STRINGS



class UtilsTest(unittest.TestCase):
    '''Class that contains test cases for fuzzing utils module'''
    @staticmethod
    def test_clean_name():
        '''Run randomly generated strings through utils.clean_name'''
        keywords = [x[0] for x in MAPPED_STRINGS]
        num_keywords = len(keywords)
        for _ in range(100):
            name_length = random.randint(1, 128)
            test_name = ''
            while len(test_name) < name_length:
                if random.random() < 1. / num_keywords:
                    test_name += random.choice(keywords)
                else:
                    test_name += random.choice(string.printable)
            clean_name(test_name)
