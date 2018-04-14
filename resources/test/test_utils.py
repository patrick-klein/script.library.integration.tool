#!/usr/bin/python
# -*- coding: utf-8 -*-
''' Defines class for testing utils module '''

import unittest

import xbmcaddon

import resources.lib.utils as utils

MANAGED_FOLDER = utils.MANAGED_FOLDER

class UtilsTest(unittest.TestCase):
    ''' Class that contains test cases for testing utils module '''

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_constants(self):
        ''' check values returned by utils constants '''
        addon = xbmcaddon.Addon(id='script.library.integration.tool')
        self.assertEqual(utils.STR_ADDON_NAME, addon.getAddonInfo('name'))
        self.assertEqual(utils.STR_ADDON_VER, addon.getAddonInfo('version'))
        self.assertEqual(utils.MANAGED_FOLDER, addon.getSetting('managed_folder'))

    def test_clean_name(self):
        ''' test all keywords in clean_name '''
        test_names = {'test1.':'test1',
                      'test2:':'test2',
                      'test3/':'test3',
                      'test4"':'test4',
                      'test5 Part 1':'test5 Part One',
                      'test6 Part 2':'test6 Part Two',
                      'test7 Part 3':'test7 Part Three',
                      'test8 Part 4':'test8 Part Four',
                      'test9 Part 5':'test9 Part Five',
                      'test10 Part 6':'test10 Part Six',
                      'test11 [cc]':'test11',
                      'test12.:/"Part 1Part 5Part 6 [cc]':
                      'test12Part OnePart FivePart Six'
                     }
        for key, value in test_names.iteritems():
            self.assertEqual(utils.clean_name(key), value)
