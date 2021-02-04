#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Defines the ManagedTVMenu class
'''

import xbmcgui
import xbmc
import resources.lib.utils as utils
from resources.lib.database_handler import DatabaseHandler


class ManagedTVMenu(object):
    ''' Provide windows for displaying managed shows and episodes,
    and tools for manipulating the objects and managed file '''

    def __init__(self):
        self.dbh = DatabaseHandler()

    @staticmethod
    @utils.logged_function
    def move_episodes_to_staged(items):
        ''' Remove all managed episodes in specified show from library, and add them to staged '''
        STR_MOVING_ALL_x_EPISODES_BACK_TO_STAGED = utils.ADDON.getLocalizedString(32034)
        STR_ALL_x_EPISODES_MOVED_TO_STAGED = utils.ADDON.getLocalizedString(32035)
        show_title = items[0].show_title
        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create(
            utils.ADDON_NAME, STR_MOVING_ALL_x_EPISODES_BACK_TO_STAGED % show_title
        )
        for index, item in enumerate(items):
            percent = 100 * index / len(items)
            progress_dialog.update(percent, line2=item.show_title, line3=item.episode_title_with_id)

            xbmc.sleep(1000)
            item.remove_from_library()
            item.set_as_staged()
        progress_dialog.close()
        utils.notification(STR_ALL_x_EPISODES_MOVED_TO_STAGED % show_title)

    @staticmethod
    @utils.logged_function
    def remove_episodes(items):
        ''' Remove all episodes in specified show from library '''
        STR_REMOVING_ALL_x_EPISODES = utils.ADDON.getLocalizedString(32032)
        STR_ALL_x_EPISODES_REMOVED = utils.ADDON.getLocalizedString(32033)
        show_title = items[0].show_title
        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create(utils.ADDON_NAME, STR_REMOVING_ALL_x_EPISODES % show_title)
        for index, item in enumerate(items):
            percent = 100 * index / len(items)
            progress_dialog.update(percent, line2=item.show_title, line3=item.episode_title_with_id)

            item.remove_from_library()
            item.delete()
        progress_dialog.close()
        utils.notification(STR_ALL_x_EPISODES_REMOVED % show_title)

    @utils.logged_function
    def episode_options(self, item):
        ''' Provide options for a single managed episode in a dialog window '''
        STR_REMOVE = utils.ADDON.getLocalizedString(32017)
        STR_MOVE_BACK_TO_STAGED = utils.ADDON.getLocalizedString(32018)
        STR_BACK = utils.ADDON.getLocalizedString(32011)
        STR_MANAGED_EPISODE_OPTIONS = utils.ADDON.getLocalizedString(32036)
        lines = [STR_REMOVE, STR_MOVE_BACK_TO_STAGED, STR_BACK]
        ret = xbmcgui.Dialog().select(
            '{0} - {1} - {2}'.format(utils.ADDON_NAME, STR_MANAGED_EPISODE_OPTIONS, item.episode_title_with_id),
            lines
        )
        if ret >= 0:
            if lines[ret] == STR_REMOVE:
                item.remove_from_library()
                item.delete()
                return self.view_episodes(item.show_title)
            elif lines[ret] == STR_MOVE_BACK_TO_STAGED:
                item.remove_from_library()
                item.set_as_staged()
                return self.view_episodes(item.show_title)
            elif lines[ret] == STR_BACK:
                return self.view_episodes(item.show_title)
        return self.view_episodes(item.show_title)

    @utils.logged_function
    def move_all_to_staged(self):
        ''' Remove all managed tvshow items from library, and add them to staged '''
        STR_MOVING_ALL_TV_SHOWS_BACK_TO_STAGED = utils.ADDON.getLocalizedString(32026)
        STR_ALL_TV_SHOWS_MOVED_TO_STAGED = utils.ADDON.getLocalizedString(32027)
        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create(utils.ADDON_NAME, STR_MOVING_ALL_TV_SHOWS_BACK_TO_STAGED)
        managed_tv_items = self.dbh.get_content_items(
            status='managed', mediatype='tvshow', order='Show_Title'
        )
        for index, item in enumerate(managed_tv_items):
            percent = 100 * index / len(managed_tv_items)
            progress_dialog.update(percent, line2=item.show_title, line3=item.episode_title_with_id)

            xbmc.sleep(1000)
            item.remove_from_library()
            item.set_as_staged()
        progress_dialog.close()
        utils.notification(STR_ALL_TV_SHOWS_MOVED_TO_STAGED)

    @utils.logged_function
    def remove_all(self):
        ''' Remove all managed tvshow items from library '''
        STR_REMOVING_ALL_TV_SHOWS = utils.ADDON.getLocalizedString(32024)
        STR_ALL_TV_SHOWS_REMOVED = utils.ADDON.getLocalizedString(32025)
        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create(utils.ADDON_NAME, STR_REMOVING_ALL_TV_SHOWS)
        managed_tv_items = self.dbh.get_content_items(
            status='managed', mediatype='tvshow', order='Show_Title'
        )
        for index, item in enumerate(managed_tv_items):
            percent = 100 * index / len(managed_tv_items)
            progress_dialog.update(percent, line2=item.show_title, line3=item.episode_title_with_id)

            item.remove_from_library()
            item.delete()
        progress_dialog.close()
        utils.notification(STR_ALL_TV_SHOWS_REMOVED)

    @utils.logged_function
    def view_episodes(self, show_title):
        ''' Displays all managed episodes in the specified show,
        which are selectable and lead to options.
        Also provides additional options at bottom of menu '''
        STR_NO_MANAGED_x_EPISODES = utils.ADDON.getLocalizedString(32028) % show_title
        STR_REMOVE_ALL_EPISODES = utils.ADDON.getLocalizedString(32029)
        STR_MOVE_ALL_EPISODES_BACK_TO_STAGED = utils.ADDON.getLocalizedString(32030)
        STR_BACK = utils.ADDON.getLocalizedString(32011)
        STR_MANAGED_x_EPISODES = utils.ADDON.getLocalizedString(32031) % show_title
        managed_episodes = self.dbh.get_content_items(
            status='managed', show_title=show_title, order='Title'
        )
        if not managed_episodes:
            xbmcgui.Dialog().ok(utils.ADDON_NAME, STR_NO_MANAGED_x_EPISODES)
            return self.view_shows()
        lines = [str(x) for x in managed_episodes]
        lines += [STR_REMOVE_ALL_EPISODES, STR_MOVE_ALL_EPISODES_BACK_TO_STAGED, STR_BACK]
        ret = xbmcgui.Dialog().select(
            '{0} - {1}'.format(utils.ADDON_NAME, STR_MANAGED_x_EPISODES), lines
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

    @utils.logged_function
    def view_shows(self):
        ''' Display all managed tvshows, which are selectable and lead to options.
        Also provides additional options at bottom of menu '''
        STR_NO_MANAGED_TV_SHOWS = utils.ADDON.getLocalizedString(32020)
        STR_REMOVE_ALL_TV_SHOWS = utils.ADDON.getLocalizedString(32021)
        STR_MOVE_ALL_TV_SHOWS_BACK_TO_STAGED = utils.ADDON.getLocalizedString(32022)
        STR_BACK = utils.ADDON.getLocalizedString(32011)
        STR_MANAGED_TV_SHOWS = utils.ADDON.getLocalizedString(32023)
        managed_tvshows = self.dbh.get_all_shows('managed')
        if not managed_tvshows:
            xbmcgui.Dialog().ok(utils.ADDON_NAME, STR_NO_MANAGED_TV_SHOWS)
            return
        lines = ['[B]%s[/B]' % x for x in managed_tvshows]
        lines += [STR_REMOVE_ALL_TV_SHOWS, STR_MOVE_ALL_TV_SHOWS_BACK_TO_STAGED, STR_BACK]
        ret = xbmcgui.Dialog().select(
            '{0} - {1}'.format(utils.ADDON_NAME, STR_MANAGED_TV_SHOWS), lines
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
