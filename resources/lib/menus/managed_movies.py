#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Defines the ManagedMoviesMenu class."""

from os import remove
from os import listdir
from os.path import join
from os.path import isdir

import xbmcgui

from resources import ADDON_NAME
from resources.lib.utils import MANAGED_FOLDER
from resources.lib.dialog_select import Select

from resources.lib.log import logged_function

from resources.lib.misc import bold
from resources.lib.misc import color
from resources.lib.misc import notification
from resources.lib.misc import getstring


class ManagedMoviesMenu(object):
    """
    Contain window for displaying managed movies.

    Provive tools for manipulating the objects and managed file.
    """

    # TODO: context menu for managed items in library
    # TODO: synced watched status with plugin item
    def __init__(self, database, progressdialog):
        """__init__ ManagedMoviesMenu."""
        self.database = database
        self.progressdialog = progressdialog

    @logged_function
    def move_all_to_staged(self, items):
        """Remove all managed movies from library, and add them to staged."""
        STR_MOVING_ALL_MOVIES_BACK_TO_STAGED = getstring(32015)
        self.progressdialog._create(
            msg=STR_MOVING_ALL_MOVIES_BACK_TO_STAGED
        )
        for index, item in enumerate(items):
            self.progressdialog._update(
                index / len(items),
                item.title
            )
            item.remove_from_library()
            item.set_as_staged()
        self.progressdialog._close()
        notification(STR_MOVING_ALL_MOVIES_BACK_TO_STAGED)

    @logged_function
    def remove_all(self, items):
        """Remove all managed movies from library."""
        STR_REMOVING_ALL_MOVIES = getstring(32013)
        STR_ALL_MOVIES_REMOVED = getstring(32014)
        self.progressdialog._create(
            msg=STR_REMOVING_ALL_MOVIES
        )
        for index, item in enumerate(items):
            self.progressdialog._update(
                index / len(items),
                item.title
            )
            item.remove_from_library()
            item.delete()
        self.progressdialog._close()
        notification(STR_ALL_MOVIES_REMOVED)

    @staticmethod
    @logged_function
    def clean_up_managed_metadata():
        """Remove all unused metadata."""
        STR_MOVIE_METADATA_CLEANED = getstring(32136)
        managed_movies_dir = join(MANAGED_FOLDER, 'movies')
        for movie_dir in listdir(managed_movies_dir):
            full_path = join(managed_movies_dir, movie_dir)
            if isdir(full_path):
                folder_contents = listdir(full_path)
                for filepath in folder_contents:
                    if '.nfo' in filepath:
                        remove(join(full_path, filepath))
        notification(STR_MOVIE_METADATA_CLEANED)

    @logged_function
    def generate_all_managed_metadata(self, items):
        """Generate metadata items for all managed movies."""
        STR_GENERATING_ALL_MOVIE_METADATA = getstring(32046)
        STR_ALL_MOVIE_METADTA_CREATED = getstring(32047)
        self.progressdialog._create(
            msg=STR_GENERATING_ALL_MOVIE_METADATA
        )
        for index, item in enumerate(items):
            self.progressdialog._update(
                index / len(items),
                item.title
            )
            item.create_metadata_item()
        self.progressdialog._close()
        notification(STR_ALL_MOVIE_METADTA_CREATED)

    @logged_function
    def options(self, item):
        """Provide options for a single managed movie in a dialog window."""
        # TODO: add rename option
        # TODO: add reload metadata option
        STR_REMOVE = getstring(32017)
        STR_MOVE_BACK_TO_STAGED = getstring(32018)
        STR_GENERATE_METADATA_ITEM = getstring(32052)
        STR_BACK = getstring(32011)
        STR_MANAGED_MOVIE_OPTIONS = getstring(32019)
        lines = [
            STR_REMOVE,
            STR_MOVE_BACK_TO_STAGED,
            STR_GENERATE_METADATA_ITEM,
            STR_BACK
        ]
        ret = xbmcgui.Dialog().select(
            '{0} - {1} - {2}'.format(
                ADDON_NAME,
                STR_MANAGED_MOVIE_OPTIONS,
                bold(color(item.title, colorname='skyblue'))
            ), lines
        )
        if ret >= 0:
            if lines[ret] == STR_REMOVE:
                item.remove_from_library()
                item.delete()
                return self.view_all()
            elif lines[ret] == STR_MOVE_BACK_TO_STAGED:
                item.remove_from_library()
                item.set_as_staged()
                return self.view_all()
            elif lines[ret] == STR_GENERATE_METADATA_ITEM:
                item.create_metadata_item()
                self.options(item)
            elif lines[ret] == STR_BACK:
                return self.view_all()
        return self.view_all()

    def view_all(self):
        """
        Display all managed movies, which are selectable and lead to options.

        Also provides additional options at bottom of menu.
        """
        STR_NO_MANAGED_MOVIES = getstring(32008)
        STR_MANAGED_MOVIES = getstring(32002)
        OPTIONS = {
            32009: self.remove_all,
            32010: self.move_all_to_staged,
            32040: self.generate_all_managed_metadata,
            32174: self.clean_up_managed_metadata,
        }
        managed_movies = list(
            self.database.get_content_items(
                status='managed',
                _type='movie'
            )
        )
        sel = Select(
            heading='{0} - {1}'.format(
                ADDON_NAME,
                STR_MANAGED_MOVIES
            )
        )
        sel.items([str(x) for x in managed_movies])
        sel.extraopts([getstring(x) for x in OPTIONS])
        if not managed_movies:
            xbmcgui.Dialog().ok(
                ADDON_NAME,
                STR_NO_MANAGED_MOVIES
            )
            return
        selection = sel.show(
            useDetails=False,
            preselect=False,
            back=True,
            back_value=getstring(32011)
        )
        if selection:
            if selection['type'] == 'item':
                self.options(managed_movies[selection['index1']])
            elif selection['type'] == 'opt':
                command = OPTIONS[list(OPTIONS.keys())[selection['index1']]]
                command(managed_movies)
