# -*- coding: utf-8 -*-

"""Defines the StagedMoviesMenu class."""

import xbmcgui

from resources import ADDON_NAME

from resources.lib.log import logged_function

from resources.lib.misc import getstring
from resources.lib.misc import notification


class StagedMoviesMenu():
    """Provide windows for displaying staged movies, and tools for managing the items."""

    # TODO: don't commit sql changes for "... all" until end
    # TODO: decorator for "...all" commands
    # TODO: load staged movies on init, use as instance variable, refresh as needed

    def __init__(self, database, progressdialog):
        """__init__ StagedMoviesMenu."""
        self.database = database
        self.progressdialog = progressdialog

    @logged_function
    def add_all(self, items):
        """Add all staged movies to library."""
        STR_ADDING_ALL_MOVIES = getstring(32042)
        STR_ALL_MOVIES_ADDED = getstring(32043)
        self.progressdialog._create(
            msg=STR_ADDING_ALL_MOVIES
        )
        for index, item in enumerate(items):
            self.progressdialog._update(
                index / len(items),
                item.title
            )
            item.add_to_library()
        self.progressdialog._close()
        notification(STR_ALL_MOVIES_ADDED)

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
        STR_ADD = getstring(32048)
        STR_REMOVE = getstring(32017)
        STR_REMOVE_AND_BLOCK = getstring(32049)
        STR_RENAME = getstring(32050)
        STR_STAGED_MOVIE_OPTIONS = getstring(32053)
        STR_BACK = getstring(32011)
        lines = [
            STR_ADD,
            STR_REMOVE,
            STR_REMOVE_AND_BLOCK,
            # STR_RENAME,
            STR_BACK
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
            elif lines[ret] == STR_BACK:
                return

        else:
            self.view_all()

    @logged_function
    def remove_all(self):
        """Remove all staged movies."""
        STR_REMOVING_ALL_MOVIES = getstring(32013)
        STR_ALL_MOVIES_REMOVED = getstring(32014)
        self.progressdialog._create(
            msg=STR_REMOVING_ALL_MOVIES
        )
        self.database.delete_item_from_table_with_status_or_showtitle(
            _type='movie',
            status='staged'
        )
        self.progressdialog._close()
        notification(STR_ALL_MOVIES_REMOVED)

    @logged_function
    def view_all(self):
        """
        Display all staged movies, which are selectable and lead to options.

        Also provides additional options at bottom of menu.
        """
        STR_NO_STAGED_MOVIES = getstring(32037)
        STR_ADD_ALL_MOVIES = getstring(32038)
        STR_REMOVE_ALL_MOVIES = getstring(32009)
        STR_BACK = getstring(32011)
        STR_STAGED_MOVIES = getstring(32004)
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
            STR_ADD_ALL_MOVIES,
            STR_REMOVE_ALL_MOVIES,
            STR_BACK
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
            elif lines[ret] == STR_REMOVE_ALL_MOVIES:
                self.remove_all()
            elif lines[ret] == STR_BACK:
                return
