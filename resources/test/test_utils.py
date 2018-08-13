#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Defines class for testing utils module
'''

import unittest

import xbmcaddon

import resources.lib.utils as utils


class TestUtils(unittest.TestCase):
    ''' Test cases for utils module '''

    def test_constants(self):
        ''' Check values returned by constants in utils '''
        addon = xbmcaddon.Addon(id='script.library.integration.tool')
        self.assertEqual(utils.ADDON_NAME, addon.getAddonInfo('name'))
        self.assertEqual(utils.ADDON_VERSION, addon.getAddonInfo('version'))
        # TODO: test all contants, including type

    def test_clean_name(self):
        ''' Test keywords in clean_name '''
        # TODO: Use MAPPED_STRINGS here
        test_names = {
            'test1.': 'test1',
            'test2:': 'test2',
            'test3/': 'test3',
            'test4"': 'test4',
            'test5 Part 1': 'test5 Part One',
            'test6 Part 2': 'test6 Part Two',
            'test7 Part 3': 'test7 Part Three',
            'test8 Part 4': 'test8 Part Four',
            'test9 Part 5': 'test9 Part Five',
            'test10 Part 6': 'test10 Part Six',
            'test11 [cc]': 'test11',
            'test12.:/"Part 1Part 5Part 6 [cc]': 'test12Part OnePart FivePart Six',
            'test13é': 'test13e',
            'test14$': 'test14',
        }
        for key, value in test_names.iteritems():
            self.assertEqual(utils.clean_name(key), value)

    def test_version_comparison(self):
        ''' Test the comparison operators for the Version class '''
        reference = utils.Version('1.2.3')
        self.assertEqual(reference, '1.2.3')
        self.assertNotEqual(reference, '3.2.1')
        self.assertGreater(reference, '0.10.0')
        self.assertLess(reference, '1.10.0')
        self.assertGreaterEqual(reference, '1.2.3')
        self.assertGreaterEqual(reference, '1.2.2')
        self.assertLessEqual(reference, '1.2.3')
        self.assertLessEqual(reference, '1.2.4')
