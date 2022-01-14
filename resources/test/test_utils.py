#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Defines class for testing utils module."""

import os

from os.path import dirname

import unittest
from resources.lib import log
from resources.lib.filesystem import delete_strm, isdir, join, removedirs

import xbmcvfs
import xbmcaddon

from resources.lib.version import Version
from resources.lib.manipulator import Cleaner

from resources import ADDON_NAME
from resources import ADDON_VERSION

from resources.lib.database import Database
from resources.lib.log import log_msg, logged_function
from resources.lib.misc import notification, re_search

WORK_DIR = dirname(__file__)


TESTE_MOVIE_QUERY = '''
                        INSERT OR IGNORE INTO
                            "movie"
                            ("file", "title", "type", "status", "year")
                        VALUES
                            (
                                'plugin://plugin.video.amazon-test/?mode=PlayVideo&name=123_movie',
                                'A Vida em um Ano',
                                'movie',
                                'staged',
                                '2020'
                            )
                    '''

TESTE_SHOW_QUERY = '''
                        INSERT OR IGNORE INTO
                            "tvshow"
                            (
                                "file", "title", "type", "status", "year", "showtitle", "season", "episode"
                            )
                        VALUES
                            (
                                'plugin://plugin.video.amazon-test/?mode=PlayVideo&name=xyz_tvshow',
                                'Abram-se as cortinas',
                                'tvshow',
                                'staged',
                                '2019',
                                'Karakuri Circus',
                                '1',
                                '1'
                            );
                    '''
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
    def test_isdir(self):
        """Teste isdir function."""
        TEST_DIRS = {
            'full': join([WORK_DIR, "full", "imaginary tvshow", "Season 1"]),
            'empty': join([WORK_DIR, "empty"]),
            'file': join([WORK_DIR, "test_isdir.txt"], True),
        }
        full_created_dir = xbmcvfs.mkdirs(TEST_DIRS['full'])
        empty_created_dir = xbmcvfs.mkdirs(TEST_DIRS['empty'])
        test_isdir_txt = open(TEST_DIRS['file'], 'w', encoding='utf-8')

        self.assertEqual(full_created_dir, True)
        self.assertEqual(empty_created_dir, True)

        if full_created_dir:
            self.assertEqual(isdir(TEST_DIRS['full']), True)
            notification(f"full_created_dir: {isdir(dirname(dirname(TEST_DIRS['full'])))}")

        if empty_created_dir:
            self.assertEqual(isdir(TEST_DIRS['empty']), True)
            notification(f"empty_created_dir: {isdir(TEST_DIRS['empty'])}")

        if test_isdir_txt:
            self.assertEqual(isdir(TEST_DIRS['file']), False)
            notification(
                f"empty_created_dir: {isdir(TEST_DIRS['file'])}"
            )

        open(join([TEST_DIRS['full'], "teste0.txt"], True), "w", encoding="utf-8")
        open(join([dirname(dirname(TEST_DIRS['full'])), "teste1.txt"], True), "w", encoding="utf-8")
        fullpath_base_dir = dirname(dirname(dirname(TEST_DIRS['full'])))
        self.assertEqual(
            xbmcvfs.rmdir(
                TEST_DIRS['empty']
            ),
            True
        )
        self.assertEqual(
            xbmcvfs.delete(
                TEST_DIRS['file']
            ),
            True
        )

        for item in "abcdefgh":
            strm_path = f"{join([fullpath_base_dir, item], True)}.strm"
            xbmcvfs.File(strm_path, "w+").write('teste')
        delete_strm(fullpath_base_dir)
        # removedirs(fullpath_base_dir)
        # self.assertEqual(xbmcvfs.existis(fullpath_base_dir), False)



    @logged_function
    def test_xbmcvfs(self):
        """test xbmcvfs."""
        VALID_FILE_PATH = join([WORK_DIR, "valid_file_path.txt"], True)
        VALID_DIR_PATH = join([WORK_DIR, "teste_dir"])
        log_msg(f"VALID_FILE_PATH {VALID_FILE_PATH}")
        log_msg(f"VALID_DIR_PATH {VALID_DIR_PATH}")

        # Teste if not exist file
        self.assertEqual(os.path.exists(VALID_FILE_PATH), False)
        self.assertEqual(xbmcvfs.exists(VALID_FILE_PATH), False)

        # Teste if not exist dir
        # self.assertEqual(os.path.exists(VALID_DIR_PATH), False)
        self.assertEqual(xbmcvfs.exists(VALID_DIR_PATH), False)
        log_msg(f"VALID_FILE_PATH not exist: {VALID_FILE_PATH}")

        with open(VALID_FILE_PATH, "w", encoding="utf-8") as valid_file_path:
            valid_file_path.write('teste')
            log_msg(f"VALID_FILE_PATH created: {VALID_FILE_PATH}")
            valid_file_path.close()

        # Teste if exist
        self.assertEqual(os.path.exists(VALID_FILE_PATH), True)
        self.assertEqual(xbmcvfs.exists(VALID_FILE_PATH), True)

        os.makedirs(VALID_DIR_PATH, exist_ok=True)
        # Teste if exist
        self.assertEqual(os.path.exists(VALID_DIR_PATH), True)
        self.assertEqual(xbmcvfs.exists(VALID_DIR_PATH), True)

        self.assertEqual(os.path.isfile(VALID_FILE_PATH), True)
        os.remove(VALID_FILE_PATH)
        os.removedirs(VALID_DIR_PATH)


    @logged_function
    def test_title_cleaner(self):
        """Test cleaner function."""

        cleaner = Cleaner()
        # db = Database()
        # db.cur.execute(TITLE_CLEAR_TEST)
        # db.conn.commit()
        TITLES = {
            'good_title': 'A Última Pessoa',
            'bad_title': 'To Your Eternity (Portuguese Dub) #1 - A Última Pessoa',
            'good_showtitle': 'To Your Eternity',
            'bad_showtitle': 'To Your Eternity (Portuguese Dub)',
        }
        self.assertEqual(
            cleaner.title(
            TITLES['bad_title'],
            TITLES['bad_showtitle']),
            TITLES['good_title']
        )
        self.assertEqual(
            cleaner.showtitle(
                TITLES['bad_showtitle']
            ),
            TITLES['good_showtitle']
        )
        # # # # # # # # # # # # # # # # # # # # # # #
        # test_names = {
        #     'test1.': 'test1',
        #     'test2:': 'test2',
        #     'test3/': 'test3',
        #     'test4"': 'test4',
        #     'test5 Part 1': 'test5 Part One',
        #     'test6 Part 2': 'test6 Part Two',
        #     'test7 Part 3': 'test7 Part Three',
        #     'test8 Part 4': 'test8 Part Four',
        #     'test9 Part 5': 'test9 Part Five',
        #     'test10 Part 6': 'test10 Part Six',
        #     'test11 [cc]': 'test11',
        #     'test12.:/"Part 1Part 5Part 6 [cc]': 'test12Part OnePart FivePart Six',
        #     'test13é': 'test13e',
        #     'test14$': 'test14',
        # }
        # for key, value in test_names.items():
        #     self.assertEqual(clean_name(key), value)

    @logged_function
    def test_db_if_is_blocked(self):
        """Teste if item if blocked."""

        db = Database()
        db.cur.execute(TESTE_BLOCKED_QUERY)
        db.conn.commit()
        FAKE_BLOCK_TESTE = {
            'exist': 'I exist and need to be finded',
            'notexit': 'I dont exit and need be ignored',
        }
        self.assertEqual(db.check_if_is_blocked(
                FAKE_BLOCK_TESTE['exist']
            ),
                True
            )
        self.assertEqual(db.check_if_is_blocked(
                FAKE_BLOCK_TESTE['notexit']
            ),
                None
        )
        db.delete_entrie_from_blocked(FAKE_BLOCK_TESTE['exist'], 'tvshow')

    @logged_function
    def test_db_path_exists(self):
        """Teste if path exist in db."""

        db = Database()
        db.cur.execute(TESTE_MOVIE_QUERY)
        db.cur.execute(TESTE_SHOW_QUERY)
        db.conn.commit()

        # ['movie', 'tvshow']
        FAKE_FILE_TESTE = {
            'movie': 'plugin://plugin.video.amazon-test/?mode=PlayVideo&name=123_movie',
            'tvshow': 'plugin://plugin.video.amazon-test/?mode=PlayVideo&name=xyz_tvshow',
            'notexit': 'plugin://plugin.video.amazon-test/?mode=PlayVideo&name=klx_not_exit',
        }
        self.assertEqual(db.path_exists(
            FAKE_FILE_TESTE['movie']), ['movie', 'staged'])
        self.assertEqual(db.path_exists(
            FAKE_FILE_TESTE['tvshow']), ['tvshow', 'staged'])
        self.assertEqual(db.path_exists(
            FAKE_FILE_TESTE['notexit']), None)
        db.delete_item_from_table('movie', FAKE_FILE_TESTE['movie'])
        db.delete_item_from_table('tvshow', FAKE_FILE_TESTE['tvshow'])

    @logged_function
    def test_re_search(self):
        """Teste re_search function."""

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
        self.assertEqual(
            re_search(
                item['type'],
                ['unknown']
            ),
            True
        )
        self.assertEqual(
            re_search(item2['type'], ['tvshow']), True)
        self.assertEqual(
            re_search(item['type'], ['unknown', 'tvshow']), True)
        self.assertEqual(
            re_search(item['label'], ['season', 'temporada', r'S\d{1,4}']), True)
        self.assertEqual(re_search(item3['label'], [
                         'season', 'temporada', r'S\d{1,4}']), True)

        self.assertNotEqual(re_search(item['type'], ['Xunknown']), True)
        self.assertNotEqual(re_search(item2['type'], ['Xtvshow']), True)
        self.assertNotEqual(
            re_search(item['type'], ['Xunknown', 'Xtvshow']), True)

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
