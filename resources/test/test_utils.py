#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Defines class for testing utils module."""

from resources.lib.log import logged_function
import unittest
import xbmcaddon  # pylint: disable=import-error

from resources.lib.version import Version
from resources.lib.utils import re_search
from resources.lib.manipulator import clean_name

from resources import ADDON_NAME, ADDON_VERSION

from resources.lib.database import Database
from resources.lib.log import logged_function

TESTE_BLOCKED_QUERY = '''
                        INSERT OR IGNORE INTO
                            "main"."blocked"
                            ("value", "type")
                        VALUES
                            (
                                'I exist and need to be finded', 'tvshow'
                            );
                    '''


class TestUtils(unittest.TestCase):
    """Test cases for utils module."""
    @logged_function
    def test_db_if_is_blocked(self):
        db = Database()
        db.cur.execute(TESTE_BLOCKED_QUERY)
        db.conn.commit()
        FAKE_BLOCK_TESTE = {
            'exist': 'I exist and need to be finded',
            'notexit': 'I dont exit and need be ignored',
        }
        self.assertEqual(db.check_if_is_blocked(FAKE_BLOCK_TESTE['exist']), True)
        self.assertEqual(db.check_if_is_blocked(FAKE_BLOCK_TESTE['notexit']), None)
        db.delete_entrie_from_blocked(FAKE_BLOCK_TESTE['exist'], 'tvshow')

    @logged_function
    def test_re_search(self):
        item = {
            "type": "unknown",
            "label": "Karakuri Circus Season 1",

        }
        item2 = {
            "type": "tvshow",
            "label": "Karakuri Circus",
        }
        item3 = {
            "type": "tvshow",
            "label": "Karakuri Circus S01",
        }
        self.assertEqual(re_search(item['type'], ['unknown']), True)
        self.assertEqual(re_search(item2['type'], ['tvshow']), True)
        self.assertEqual(re_search(item['type'], ['unknown', 'tvshow']), True)
        self.assertEqual(re_search(item['label'], ['season', 'temporada', r'S\d{1,4}']), True)
        self.assertEqual(re_search(item3['label'], [
                         'season', 'temporada', r'S\d{1,4}']), True)

        self.assertNotEqual(re_search(item['type'], ['Xunknown']), True)
        self.assertNotEqual(re_search(item2['type'], ['Xtvshow']), True)
        self.assertNotEqual(re_search(item['type'], ['Xunknown', 'Xtvshow']), True)

        self.assertNotEqual(
            re_search(item2['label'], ['season', 'temporada', r'S\d{1,4}']), True)


    @logged_function
    def test_constants(self):
        """Check values returned by constants in utils."""
        addon = xbmcaddon.Addon(id='script.library.integration.tool')
        self.assertEqual(
            ADDON_NAME,
            addon.getAddonInfo('name')
        )
        self.assertEqual(
            ADDON_VERSION,
            addon.getAddonInfo('version')
        )
        # TODO: test all contants, including type

    @logged_function
    def test_clean_name(self):
        """Test keywords in clean_name."""
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
        for key, value in test_names.items():
            self.assertEqual(clean_name(key), value)

    @logged_function
    def test_version_comparison(self):
        """Test the comparison operators for the Version class."""
        reference = Version('1.2.3')
        self.assertEqual(reference, '1.2.3')
        self.assertNotEqual(reference, '3.2.1')
        self.assertGreater(reference, '0.10.0')
        self.assertLess(reference, '1.10.0')
        self.assertGreaterEqual(reference, '1.2.3')
        self.assertGreaterEqual(reference, '1.2.2')
        self.assertLessEqual(reference, '1.2.3')
        self.assertLessEqual(reference, '1.2.4')
