#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Defines the ManagedMoviesMenu class
'''

import xbmcgui

import resources.lib.utils as utils
from resources.lib.database_handler import DatabaseHandler


class ManagedMoviesMenu(object):
    ''' Provide windows for displaying managed movies,
    and tools for manipulating the objects and managed file '''

    # TODO: context menu for managed items in library
    # TODO: synced watched status with plugin item

    def __init__(self):
        self.dbh = DatabaseHandler()

    @staticmethod
    @utils.logged_function
    def move_all_to_staged(items):
        ''' Remove all managed movies from library, and add them to staged '''
        STR_MOVING_ALL_MOVIES_BACK_TO_STAGED = utils.ADDON.getLocalizedString(32015)
        STR_ALL_MOVIES_MOVED_TO_STAGED = utils.ADDON.getLocalizedString(32016)
        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create(utils.ADDON_NAME, STR_MOVING_ALL_MOVIES_BACK_TO_STAGED)
        for index, item in enumerate(items):
            percent = 100 * index / len(items)
            progress_dialog.update(percent, line2=item.movie_title)
            item.remove_from_library()
            item.set_as_staged()
        progress_dialog.close()
        utils.notification(STR_ALL_MOVIES_MOVED_TO_STAGED)

    @staticmethod
    @utils.logged_function
    def remove_all(items):
        ''' Remove all managed movies from library '''
        STR_REMOVING_ALL_MOVIES = utils.ADDON.getLocalizedString(32013)
        STR_ALL_MOVIES_REMOVED = utils.ADDON.getLocalizedString(32014)
        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create(utils.ADDON_NAME, STR_REMOVING_ALL_MOVIES)
        for index, item in enumerate(items):
            percent = 100 * index / len(items)
            progress_dialog.update(percent, line2=item.movie_title)
            item.remove_from_library()
            item.delete()
        progress_dialog.close()
        utils.notification(STR_ALL_MOVIES_REMOVED)

    @utils.logged_function
    def options(self, item):
        ''' Provide options for a single managed movie in a dialog window '''
        # TODO: add rename option
        # TODO: add reload metadata option
        STR_REMOVE = utils.ADDON.getLocalizedString(32017)
        STR_MOVE_BACK_TO_STAGED = utils.ADDON.getLocalizedString(32018)
        STR_BACK = utils.ADDON.getLocalizedString(32011)
        STR_MANAGED_MOVIE_OPTIONS = utils.ADDON.getLocalizedString(32019)
        lines = [STR_REMOVE, STR_MOVE_BACK_TO_STAGED, STR_BACK]
        ret = xbmcgui.Dialog().select(
            '{0} - {1} - {2}'.format(
                utils.ADDON_NAME, STR_MANAGED_MOVIE_OPTIONS,
                item.movie_title
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
            elif lines[ret] == STR_BACK:
                return self.view_all()
        return self.view_all()

    def view_all(self):
        ''' Display all managed movies, which are selectable and lead to options.
        Also provides additional options at bottom of menu '''
        STR_NO_MANAGED_MOVIES = utils.ADDON.getLocalizedString(32008)
        STR_REMOVE_ALL_MOVIES = utils.ADDON.getLocalizedString(32009)
        STR_MOVE_ALL_BACK_TO_STAGED = utils.ADDON.getLocalizedString(32010)
        STR_BACK = utils.ADDON.getLocalizedString(32011)
        STR_MANAGED_MOVIES = utils.ADDON.getLocalizedString(32012)

        managed_movies = self.dbh.get_content_items(
            status='managed', mediatype='movie', order='Title'
        )

        if not managed_movies:
            xbmcgui.Dialog().ok(utils.ADDON_NAME, STR_NO_MANAGED_MOVIES)
            return

        lines = [str(x) for x in managed_movies]
        lines += [STR_REMOVE_ALL_MOVIES, STR_MOVE_ALL_BACK_TO_STAGED, STR_BACK]
        ret = xbmcgui.Dialog().select(
            '{0} - {1}'.format(utils.ADDON_NAME, STR_MANAGED_MOVIES), lines
        )
        if ret >= 0:
            if ret < len(managed_movies):
                for i, item in enumerate(managed_movies):
                    if ret == i:
                        self.options(item)
                        break
            elif lines[ret] == STR_REMOVE_ALL_MOVIES:
                self.remove_all(managed_movies)
            elif lines[ret] == STR_MOVE_ALL_BACK_TO_STAGED:
                self.move_all_to_staged(managed_movies)
            elif lines[ret] == STR_BACK:
                return
