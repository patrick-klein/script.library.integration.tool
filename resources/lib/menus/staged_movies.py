#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Defines the StagedMoviesMenu class."""

import os
import shutil
from fnmatch import fnmatch

import xbmc  # pylint: disable=import-error
import xbmcgui  # pylint: disable=import-error


from resources import ADDON_NAME
from resources.lib.log import log_msg
from resources.lib.log import logged_function

from resources.lib.utils import notification
from resources.lib.utils import METADATA_FOLDER
from resources.lib.utils import getlocalizedstring


class StagedMoviesMenu(object):
    """Provide windows for displaying staged movies, and tools for managing the items."""

    # TODO: don't commit sql changes for "... all" until end
    # TODO: decorator for "...all" commands
    # TODO: load staged movies on init, use as instance variable, refresh as needed

    def __init__(self, database):
        """__init__ StagedMoviesMenu."""
        self.database = database
        self.progressdialog = xbmcgui.DialogProgress()

    @logged_function
    def add_all(self, items):
        """Add all staged movies to library."""
        STR_ADDING_ALL_MOVIES = getlocalizedstring(32042)
        STR_ALL_MOVIES_ADDED = getlocalizedstring(32043)
        self.progressdialog.create(
            ADDON_NAME,
            STR_ADDING_ALL_MOVIES
        )
        for index, item in enumerate(items):
            percent = 100 * index / len(items)
            self.progressdialog.update(
                int(percent),
                item.title
            )
            item.add_to_library()
        self.progressdialog.close()
        notification(STR_ALL_MOVIES_ADDED)

    @logged_function
    def add_all_with_metadata(self, items):
        """Add all movies with nfo files to the library."""
        # TODO: Remove code duplication with MovieItem.add_to_library_if_metadata
        STR_ADDING_ALL_MOVIES_WITH_METADATA = getlocalizedstring(32044)
        STR_ALL_MOVIES_WITH_METADTA_ADDED = getlocalizedstring(32045)
        self.progressdialog.create(
            ADDON_NAME,
            STR_ADDING_ALL_MOVIES_WITH_METADATA
        )
        for index, item in enumerate(items):
            percent = 100 * index / len(items)
            if os.path.exists(item.movie_nfo[0]):
                self.progressdialog.update(
                    int(percent),
                    item.title
                )
                item.add_to_library()
            # self.progressdialog.update(int(percent), ' ') # TODO: remove it?
        self.progressdialog.close()
        notification(STR_ALL_MOVIES_WITH_METADTA_ADDED)

    @staticmethod
    @logged_function
    def clean_up_metadata():
        """Remove all unused metadata."""
        STR_MOVIE_METADATA_CLEANED = getlocalizedstring(32136)
        metadata_dir = os.path.join(METADATA_FOLDER, 'Movies')
        for folder in os.listdir(metadata_dir):
            full_path = os.path.join(metadata_dir, folder)
            if os.path.isdir(full_path):
                folder_contents = os.listdir(full_path)
                if len(folder_contents) == 1 and fnmatch(folder_contents[0], '*.strm'):
                    log_msg(
                        'Removing metadata folder {}'.format(full_path), loglevel=xbmc.LOGINFO
                    )
                shutil.rmtree(full_path)
        notification(STR_MOVIE_METADATA_CLEANED)

    @logged_function
    def generate_all_metadata(self, items):
        """Generate metadata items for all staged movies."""
        STR_GENERATING_ALL_MOVIE_METADATA = getlocalizedstring(32046)
        STR_ALL_MOVIE_METADTA_CREATED = getlocalizedstring(32047)
        self.progressdialog.create(
            ADDON_NAME,
            STR_GENERATING_ALL_MOVIE_METADATA
        )
        for index, item in enumerate(items):
            percent = 100 * index / len(items)
            self.progressdialog.update(
                int(percent),
                item.title
            )
            item.create_metadata_item()
        self.progressdialog.close()
        notification(STR_ALL_MOVIE_METADTA_CREATED)

    @staticmethod
    def rename_dialog(item):
        """Prompt input for new name, and rename if non-empty string."""
        # TODO: move to utils or parent class so it's not duplicated
        input_ret = xbmcgui.Dialog().input(
            "Title",
            defaultt=item.title
        )
        if input_ret:
            item.rename(input_ret)

    @logged_function
    def options(self, item):
        """Provide options for a single staged movie in a dialog window."""
        # TODO: add a back button
        STR_ADD = getlocalizedstring(32048)
        STR_REMOVE = getlocalizedstring(32017)
        STR_REMOVE_AND_BLOCK = getlocalizedstring(32049)
        STR_RENAME = getlocalizedstring(32050)
        STR_AUTOMATICALLY_RENAME_USING_METADTA = getlocalizedstring(32051)
        STR_GENERATE_METADATA_ITEM = getlocalizedstring(32052)
        STR_STAGED_MOVIE_OPTIONS = getlocalizedstring(32053)
        lines = [
            STR_ADD,
            STR_REMOVE,
            STR_REMOVE_AND_BLOCK,
            # STR_RENAME,
            # STR_AUTOMATICALLY_RENAME_USING_METADTA,
            STR_GENERATE_METADATA_ITEM
        ]
        ret = xbmcgui.Dialog().select(
            '{0} - {1} - {2}'.format(
                ADDON_NAME,
                STR_STAGED_MOVIE_OPTIONS,
                item.title),
            lines
        )
        if ret >= 0:
            if lines[ret] == STR_ADD:
                item.add_to_library()
                self.view_all()
            elif lines[ret] == STR_REMOVE:
                item.delete()
                self.view_all()
            elif lines[ret] == STR_REMOVE_AND_BLOCK:
                item.remove_and_block()
                self.view_all()
            elif lines[ret] == STR_RENAME:
                self.rename_dialog(item)
                self.options(item)
            elif lines[ret] == STR_GENERATE_METADATA_ITEM:
                item.create_metadata_item()
                self.options(item)
            elif lines[ret] == STR_AUTOMATICALLY_RENAME_USING_METADTA:
                item.rename_using_metadata()
                self.options(item)
        else:
            self.view_all()

    @logged_function
    def remove_all(self):
        """Remove all staged movies."""
        STR_REMOVING_ALL_MOVIES = getlocalizedstring(32013)
        STR_ALL_MOVIES_REMOVED = getlocalizedstring(32014)
        self.progressdialog.create(ADDON_NAME, STR_REMOVING_ALL_MOVIES)
        self.database.remove_from(
            status='staged',
            _type='movie'
        )
        self.progressdialog.close()
        notification(STR_ALL_MOVIES_REMOVED)

    @logged_function
    def view_all(self):
        """
        Display all staged movies, which are selectable and lead to options.

        Also provides additional options at bottom of menu.
        """
        STR_NO_STAGED_MOVIES = getlocalizedstring(32037)
        STR_ADD_ALL_MOVIES = getlocalizedstring(32038)
        STR_ADD_ALL_MOVIES_WITH_METADATA = getlocalizedstring(32039)
        STR_REMOVE_ALL_MOVIES = getlocalizedstring(32009)
        STR_GENERATE_ALL_METADATA_ITEMS = getlocalizedstring(32040)
        STR_BACK = getlocalizedstring(32011)
        STR_STAGED_MOVIES = getlocalizedstring(32041)
        STR_CLEAN_UP_METADATA = getlocalizedstring(32135)
        staged_movies = list(
            self.database.get_content_items(
                status='staged',
                _type='movie'
            )
        )
        if not staged_movies:
            xbmcgui.Dialog().ok(ADDON_NAME, STR_NO_STAGED_MOVIES)
            return
        lines = [str(x) for x in staged_movies]
        lines += [
            STR_ADD_ALL_MOVIES, STR_ADD_ALL_MOVIES_WITH_METADATA, STR_REMOVE_ALL_MOVIES,
            STR_GENERATE_ALL_METADATA_ITEMS, STR_CLEAN_UP_METADATA, STR_BACK
        ]
        ret = xbmcgui.Dialog().select(
            '{0} - {1}'.format(ADDON_NAME, STR_STAGED_MOVIES), lines
        )
        if ret >= 0:
            if ret < len(staged_movies):  # staged item
                for i, item in enumerate(staged_movies):
                    if ret == i:
                        self.options(item)
                        break
            elif lines[ret] == STR_ADD_ALL_MOVIES:
                self.add_all(staged_movies)
            elif lines[ret] == STR_ADD_ALL_MOVIES_WITH_METADATA:
                self.add_all_with_metadata(staged_movies)
                self.view_all()
            elif lines[ret] == STR_REMOVE_ALL_MOVIES:
                self.remove_all()
            elif lines[ret] == STR_GENERATE_ALL_METADATA_ITEMS:
                self.generate_all_metadata(staged_movies)
                self.view_all()
            elif lines[ret] == STR_CLEAN_UP_METADATA:
                self.clean_up_metadata()
                self.view_all()
            elif lines[ret] == STR_BACK:
                return
