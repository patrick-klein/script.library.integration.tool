#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
This module contains the classes ManagedMovies and ManagedTV,
which provide dialog windows and tools for editing managed movies and tvshow items
'''

import xbmcaddon
import xbmcgui

import resources.lib.utils as utils
from .database_handler import DatabaseHandler


class ManagedMovies(object):
    '''
    Provides windows for displaying managed movies,
    and tools for manipulating the objects and managed file
    '''

    #TODO: pass around a "previous_view" function handle
    #TODO: context menu for managed items in library
    #TODO: synced watched status with plugin item

    def __init__(self):
        self.addon = xbmcaddon.Addon()
        self.STR_ADDON_NAME = self.addon.getAddonInfo('name')
        self.dbh = DatabaseHandler()

    @utils.log_decorator
    def view_all(self):
        '''
        Displays all managed movies, which are selectable and lead to options.
        Also provides additional options at bottom of menu
        '''
        STR_NO_MANAGED_MOVIES = self.addon.getLocalizedString(32008)
        STR_REMOVE_ALL_MOVIES = self.addon.getLocalizedString(32009)
        STR_MOVE_ALL_BACK_TO_STAGED = self.addon.getLocalizedString(32010)
        STR_BACK = self.addon.getLocalizedString(32011)
        STR_MANAGED_MOVIES = self.addon.getLocalizedString(32012)
        managed_movies = self.dbh.get_content_items(
            status='managed', mediatype='movie', order='Title'
        )
        if not managed_movies:
            xbmcgui.Dialog().ok(self.STR_ADDON_NAME, STR_NO_MANAGED_MOVIES)
            return
        lines = [str(x) for x in managed_movies]
        lines += [STR_REMOVE_ALL_MOVIES, STR_MOVE_ALL_BACK_TO_STAGED, STR_BACK]
        ret = xbmcgui.Dialog().select(
            '{0} - {1}'.format(self.STR_ADDON_NAME, STR_MANAGED_MOVIES), lines
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

    @utils.log_decorator
    def remove_all(self, items):
        ''' Removes all managed movies from library '''
        STR_REMOVING_ALL_MOVIES = self.addon.getLocalizedString(32013)
        STR_ALL_MOVIES_REMOVED = self.addon.getLocalizedString(32014)
        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create(self.STR_ADDON_NAME, STR_REMOVING_ALL_MOVIES)
        for item in items:
            progress_dialog.update(0, line2=item.get_title())
            item.remove_from_library()
            item.delete()
        progress_dialog.close()
        utils.notification(STR_ALL_MOVIES_REMOVED)

    @utils.log_decorator
    def move_all_to_staged(self, items):
        ''' Removes all managed movies from library, and adds them to staged '''
        STR_MOVING_ALL_MOVIES_BACK_TO_STAGED = self.addon.getLocalizedString(32015)
        STR_ALL_MOVIES_MOVED_TO_STAGED = self.addon.getLocalizedString(32016)
        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create(self.STR_ADDON_NAME, STR_MOVING_ALL_MOVIES_BACK_TO_STAGED)
        for item in items:
            progress_dialog.update(0, line2=item.get_title())
            item.remove_from_library()
            item.set_as_staged()
        progress_dialog.close()
        utils.notification(STR_ALL_MOVIES_MOVED_TO_STAGED)

    @utils.log_decorator
    def options(self, item):
        ''' Provides options for a single managed movie in a dialog window '''
        # TODO: add rename option
        # TODO: add reload metadata option
        STR_REMOVE = self.addon.getLocalizedString(32017)
        STR_MOVE_BACK_TO_STAGED = self.addon.getLocalizedString(32018)
        STR_BACK = self.addon.getLocalizedString(32011)
        STR_MANAGED_MOVIE_OPTIONS = self.addon.getLocalizedString(32019)
        lines = [STR_REMOVE, STR_MOVE_BACK_TO_STAGED, STR_BACK]
        ret = xbmcgui.Dialog().select(
            '{0} - {1} - {2}'.format(
                self.STR_ADDON_NAME, STR_MANAGED_MOVIE_OPTIONS, item.get_title()
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


class ManagedTV(object):
    '''
    Provides windows for displaying managed shows and episodes,
    and tools for manipulating the objects and managed file
    '''

    def __init__(self):
        self.addon = xbmcaddon.Addon()
        self.STR_ADDON_NAME = self.addon.getAddonInfo('name')
        self.dbh = DatabaseHandler()

    @utils.log_decorator
    def view_shows(self):
        '''
        Displays all managed tvshows, which are selectable and lead to options.
        Also provides additional options at bottom of menu
        '''
        STR_NO_MANAGED_TV_SHOWS = self.addon.getLocalizedString(32020)
        STR_REMOVE_ALL_TV_SHOWS = self.addon.getLocalizedString(32021)
        STR_MOVE_ALL_TV_SHOWS_BACK_TO_STAGED = self.addon.getLocalizedString(32022)
        STR_BACK = self.addon.getLocalizedString(32011)
        STR_MANAGED_TV_SHOWS = self.addon.getLocalizedString(32023)
        managed_tvshows = self.dbh.get_all_shows('managed')
        if not managed_tvshows:
            xbmcgui.Dialog().ok(self.STR_ADDON_NAME, STR_NO_MANAGED_TV_SHOWS)
            return
        lines = ['[B]%s[/B]' % x for x in managed_tvshows]
        lines += [STR_REMOVE_ALL_TV_SHOWS, STR_MOVE_ALL_TV_SHOWS_BACK_TO_STAGED, STR_BACK]
        ret = xbmcgui.Dialog().select(
            '{0} - {1}'.format(self.STR_ADDON_NAME, STR_MANAGED_TV_SHOWS), lines
        )
        if ret >= 0:
            if ret < len(managed_tvshows):
                for show_title in managed_tvshows:
                    if managed_tvshows[ret] == show_title:
                        self.view_episodes(show_title)
                        break
            elif lines[ret] == STR_REMOVE_ALL_TV_SHOWS:
                self.remove_all()
            elif lines[ret] == STR_MOVE_ALL_TV_SHOWS_BACK_TO_STAGED:
                self.move_all_to_staged()
            elif lines[ret] == STR_BACK:
                return

    @utils.log_decorator
    def remove_all(self):
        ''' Removes all managed tvshow items from library '''
        STR_REMOVING_ALL_TV_SHOWS = self.addon.getLocalizedString(32024)
        STR_ALL_TV_SHOWS_REMOVED = self.addon.getLocalizedString(32025)
        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create(self.STR_ADDON_NAME, STR_REMOVING_ALL_TV_SHOWS)
        managed_tv_items = self.dbh.get_content_items(
            status='managed', mediatype='tvshow', order='Show_Title'
        )
        for item in managed_tv_items:
            progress_dialog.update(0, line2=item.get_show_title(), line3=item.get_title())
            item.remove_from_library()
            item.delete()
        progress_dialog.close()
        utils.notification(STR_ALL_TV_SHOWS_REMOVED)

    @utils.log_decorator
    def move_all_to_staged(self):
        ''' Removes all managed tvshow items from library, and adds them to staged '''
        STR_MOVING_ALL_TV_SHOWS_BACK_TO_STAGED = self.addon.getLocalizedString(32026)
        STR_ALL_TV_SHOWS_MOVED_TO_STAGED = self.addon.getLocalizedString(32027)
        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create(self.STR_ADDON_NAME, STR_MOVING_ALL_TV_SHOWS_BACK_TO_STAGED)
        managed_tv_items = self.dbh.get_content_items(
            status='managed', mediatype='tvshow', order='Show_Title'
        )
        for item in managed_tv_items:
            progress_dialog.update(0, line2=item.get_show_title(), line3=item.get_title())
            item.remove_from_library()
            item.set_as_staged()
        progress_dialog.close()
        utils.notification(STR_ALL_TV_SHOWS_MOVED_TO_STAGED)

    @utils.log_decorator
    def view_episodes(self, show_title):
        '''
        Displays all managed episodes in the specified show,
        which are selectable and lead to options.
        Also provides additional options at bottom of menu.
        '''
        STR_NO_MANAGED_x_EPISODES = self.addon.getLocalizedString(32028) % show_title
        STR_REMOVE_ALL_EPISODES = self.addon.getLocalizedString(32029)
        STR_MOVE_ALL_EPISODES_BACK_TO_STAGED = self.addon.getLocalizedString(32030)
        STR_BACK = self.addon.getLocalizedString(32011)
        STR_MANAGED_x_EPISODES = self.addon.getLocalizedString(32031) % show_title
        managed_episodes = self.dbh.get_content_items(
            status='managed', show_title=show_title, order='Title'
        )
        if not managed_episodes:
            xbmcgui.Dialog().ok(self.STR_ADDON_NAME, STR_NO_MANAGED_x_EPISODES)
            return self.view_shows()
        lines = [str(x) for x in managed_episodes]
        lines += [STR_REMOVE_ALL_EPISODES, STR_MOVE_ALL_EPISODES_BACK_TO_STAGED, STR_BACK]
        ret = xbmcgui.Dialog().select(
            '{0} - {1}'.format(self.STR_ADDON_NAME, STR_MANAGED_x_EPISODES), lines
        )
        if ret >= 0:
            if ret < len(managed_episodes):  # managed item
                for i, item in enumerate(managed_episodes):
                    if ret == i:
                        return self.episode_options(item)
            elif lines[ret] == STR_REMOVE_ALL_EPISODES:
                self.remove_episodes(managed_episodes)
                return self.view_shows()
            elif lines[ret] == STR_MOVE_ALL_EPISODES_BACK_TO_STAGED:
                self.move_episodes_to_staged(managed_episodes)
                return self.view_shows()
            elif lines[ret] == STR_BACK:
                return self.view_shows()
        return self.view_shows()

    @utils.log_decorator
    def remove_episodes(self, items):
        ''' Removes all episodes in specified show from library '''
        STR_REMOVING_ALL_x_EPISODES = self.addon.getLocalizedString(32032)
        STR_ALL_x_EPISODES_REMOVED = self.addon.getLocalizedString(32033)
        show_title = items[0].get_show_title()
        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create(self.STR_ADDON_NAME, STR_REMOVING_ALL_x_EPISODES % show_title)
        for item in items:
            progress_dialog.update(0, line2=item.get_title())
            item.remove_from_library()
            item.delete()
        progress_dialog.close()
        utils.notification(STR_ALL_x_EPISODES_REMOVED % show_title)

    @utils.log_decorator
    def move_episodes_to_staged(self, items):
        ''' Removes all managed episodes in specified show from library, and adds them to staged '''
        STR_MOVING_ALL_x_EPISODES_BACK_TO_STAGED = self.addon.getLocalizedString(32034)
        STR_ALL_x_EPISODES_MOVED_TO_STAGED = self.addon.getLocalizedString(32035)
        show_title = items[0].get_show_title()
        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create(
            self.STR_ADDON_NAME, STR_MOVING_ALL_x_EPISODES_BACK_TO_STAGED % show_title
        )
        for item in items:
            progress_dialog.update(0, line2=item.get_title())
            item.remove_from_library()
            item.set_as_staged()
        progress_dialog.close()
        utils.notification(STR_ALL_x_EPISODES_MOVED_TO_STAGED % show_title)

    @utils.log_decorator
    def episode_options(self, item):
        ''' Provides options for a single managed episode in a dialog window '''
        STR_REMOVE = self.addon.getLocalizedString(32017)
        STR_MOVE_BACK_TO_STAGED = self.addon.getLocalizedString(32018)
        STR_BACK = self.addon.getLocalizedString(32011)
        STR_MANAGED_EPISODE_OPTIONS = self.addon.getLocalizedString(32036)
        lines = [STR_REMOVE, STR_MOVE_BACK_TO_STAGED, STR_BACK]
        ret = xbmcgui.Dialog().select(
            '{0} - {1} - {2}'.format(
                self.STR_ADDON_NAME, STR_MANAGED_EPISODE_OPTIONS, item.get_title()
            ), lines
        )
        if ret >= 0:
            if lines[ret] == STR_REMOVE:
                item.remove_from_library()
                item.delete()
                return self.view_episodes(item.get_show_title())
            elif lines[ret] == STR_MOVE_BACK_TO_STAGED:
                item.remove_from_library()
                item.set_as_staged()
                return self.view_episodes(item.get_show_title())
            elif lines[ret] == STR_BACK:
                return self.view_episodes(item.get_show_title())
        return self.view_episodes(item.get_show_title())
