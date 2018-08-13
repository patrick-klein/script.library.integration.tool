#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Defines the StagedTVMenu class
'''

import os.path

import xbmcgui

import resources.lib.utils as utils
from resources.lib.database_handler import DatabaseHandler


class StagedTVMenu(object):
    ''' Provide windows for displaying staged tvshows and episodes,
    and tools for managing the items '''

    def __init__(self):
        self.dbh = DatabaseHandler()

    @staticmethod
    @utils.logged_function
    def add_all_episodes(items):
        ''' Add all episodes from specified show to library '''
        STR_ADDING_ALL_x_EPISODES = utils.ADDON.getLocalizedString(32071)
        STR_ALL_x_EPISODES_ADDED = utils.ADDON.getLocalizedString(32072)
        show_title = items[0].show_title
        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create(utils.ADDON_NAME, STR_ADDING_ALL_x_EPISODES % show_title)
        for index, item in enumerate(items):
            percent = 100 * index / len(items)
            progress_dialog.update(percent, line2=item.title)
            item.add_to_library()
        progress_dialog.close()
        utils.notification(STR_ALL_x_EPISODES_ADDED % show_title)

    @staticmethod
    @utils.logged_function
    def add_all_episodes_with_metadata(items):
        ''' Add all episodes in the specified show with metadata to the library '''
        STR_ADDING_ALL_x_EPISODES_WITH_METADATA = utils.ADDON.getLocalizedString(32073)
        STR_ALL_x_EPISODES_WITH_METADATA_ADDED = utils.ADDON.getLocalizedString(32074)
        show_title = items[0].show_title
        clean_show_title = utils.clean_name(show_title)
        metadata_dir = os.path.join(utils.METADATA_FOLDER, 'TV', clean_show_title)
        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create(
            utils.ADDON_NAME, STR_ADDING_ALL_x_EPISODES_WITH_METADATA % show_title
        )
        for index, item in enumerate(items):
            percent = 100 * index / len(items)
            nfo_path = os.path.join(metadata_dir, item.clean_title + '.nfo')
            if os.path.exists(nfo_path):
                progress_dialog.update(percent, line2=item.title)
                item.add_to_library()
            progress_dialog.update(percent, line2=' ')
        progress_dialog.close()
        utils.notification(STR_ALL_x_EPISODES_WITH_METADATA_ADDED % show_title)

    @staticmethod
    @utils.logged_function
    def generate_all_episodes_metadata(items):
        ''' Generate metadata items for all episodes in show '''
        STR_GENERATING_ALL_x_METADATA = utils.ADDON.getLocalizedString(32077)
        STR_ALL_x_METADATA_CREATED = utils.ADDON.getLocalizedString(32078)
        show_title = items[0].show_title
        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create(utils.ADDON_NAME, STR_GENERATING_ALL_x_METADATA % show_title)
        for index, item in enumerate(items):
            percent = 100 * index / len(items)
            progress_dialog.update(percent, line2=item.title)
            item.create_metadata_item()
        progress_dialog.close()
        utils.notification(STR_ALL_x_METADATA_CREATED % show_title)

    @staticmethod
    def rename_dialog(item):
        ''' Prompt input for new name, and rename if non-empty string '''
        input_ret = xbmcgui.Dialog().input("Title", defaultt=item.title)
        if input_ret:
            item.rename(input_ret)

    @staticmethod
    @utils.logged_function
    def rename_episodes_using_metadata(items):
        ''' Rename all episodes in show using nfo files '''
        STR_RENAMING_x_EPISODES_USING_METADATA = utils.ADDON.getLocalizedString(32075)
        STR_x_EPISODES_RENAMED_USING_METADATA = utils.ADDON.getLocalizedString(32076)
        show_title = items[0].show_title
        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create(
            utils.ADDON_NAME, STR_RENAMING_x_EPISODES_USING_METADATA % show_title
        )
        for index, item in enumerate(items):
            percent = 100 * index / len(items)
            progress_dialog.update(percent, line2=item.title)
            item.rename_using_metadata()
        progress_dialog.close()
        utils.notification(STR_x_EPISODES_RENAMED_USING_METADATA % show_title)

    @utils.logged_function
    def add_all_shows(self):
        ''' Add all tvshow items to library '''
        STR_ADDING_ALL_TV_SHOWS = utils.ADDON.getLocalizedString(32059)
        STR_ALL_TV_SHOWS_ADDED = utils.ADDON.getLocalizedString(32060)
        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create(utils.ADDON_NAME, STR_ADDING_ALL_TV_SHOWS)
        staged_tv_items = self.dbh.get_content_items(
            status='staged', mediatype='tvshow', order='Show_Title'
        )
        for index, item in enumerate(staged_tv_items):
            percent = 100 * index / len(staged_tv_items)
            progress_dialog.update(percent, line2=item.title)
            item.add_to_library()
        progress_dialog.close()
        utils.notification(STR_ALL_TV_SHOWS_ADDED)

    @utils.logged_function
    def add_all_with_metadata(self):
        ''' Add all tvshow items with nfo file to library'''
        STR_ADDING_ALL_TV_SHOW_ITEMS_WITH_METADATA = utils.ADDON.getLocalizedString(32061)
        STR_ALL_TV_SHOW_ITEMS_WITH_METADATA_ADDED = utils.ADDON.getLocalizedString(32062)
        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create(utils.ADDON_NAME, STR_ADDING_ALL_TV_SHOW_ITEMS_WITH_METADATA)
        staged_tv_items = self.dbh.get_content_items(
            status='staged', mediatype='tvshow', order='Show_Title'
        )
        for index, item in enumerate(staged_tv_items):
            percent = 100 * index / len(staged_tv_items)
            nfo_path = os.path.join(item.metadata_dir, item.clean_title + '.nfo')
            if os.path.exists(nfo_path):
                progress_dialog.update(percent, line2=item.show_title, line3=item.title)
                item.add_to_library()
            progress_dialog.update(percent, line2=' ', line3=' ')
        progress_dialog.close()
        utils.notification(STR_ALL_TV_SHOW_ITEMS_WITH_METADATA_ADDED)

    @utils.logged_function
    def episode_options(self, item):
        ''' Provide options for a single staged episode in a dialog window '''
        #TODO: rename associated metadata when renaming
        #TODO: rename show title
        #TODO: remove item (including metadata)
        STR_ADD = utils.ADDON.getLocalizedString(32048)
        STR_REMOVE = utils.ADDON.getLocalizedString(32017)
        STR_REMOVE_AND_BLOCK_EPISODE = utils.ADDON.getLocalizedString(32079)
        STR_RENAME = utils.ADDON.getLocalizedString(32050)
        STR_AUTOMATICALLY_RENAME_USING_METADTA = utils.ADDON.getLocalizedString(32051)
        STR_GENERATE_METADATA_ITEM = utils.ADDON.getLocalizedString(32052)
        STR_BACK = utils.ADDON.getLocalizedString(32011)
        STR_STAGED_EPISODE_OPTIONS = utils.ADDON.getLocalizedString(32080)
        lines = [
            STR_ADD, STR_REMOVE, STR_REMOVE_AND_BLOCK_EPISODE, STR_RENAME,
            STR_AUTOMATICALLY_RENAME_USING_METADTA, STR_GENERATE_METADATA_ITEM, STR_BACK
        ]
        ret = xbmcgui.Dialog().select(
            '{0} - {1} - {2}'.format(utils.ADDON_NAME, STR_STAGED_EPISODE_OPTIONS, item.title),
            lines
        )
        if ret >= 0:
            if lines[ret] == STR_ADD:
                item.add_to_library()
                self.view_episodes(item.show_title)
            elif lines[ret] == STR_REMOVE:
                item.delete()
                self.view_episodes(item.show_title)
            elif lines[ret] == STR_REMOVE_AND_BLOCK_EPISODE:
                item.remove_and_block()
                self.view_episodes(item.show_title)
            elif lines[ret] == STR_RENAME:
                self.rename_dialog(item)
                self.episode_options(item)
            elif lines[ret] == STR_GENERATE_METADATA_ITEM:
                item.create_metadata_item()
                self.episode_options(item)
            elif lines[ret] == STR_AUTOMATICALLY_RENAME_USING_METADTA:
                item.rename_using_metadata()
                self.episode_options(item)
            elif lines[ret] == STR_BACK:
                self.view_episodes(item.show_title)
        else:
            self.view_episodes(item.show_title)

    @utils.logged_function
    def generate_all_metadata(self):
        ''' Create metadata for all staged tvshow items '''
        STR_GENERATING_ALL_TV_SHOW_METADATA = utils.ADDON.getLocalizedString(32063)
        STR_ALL_TV_SHOW_METADATA_CREATED = utils.ADDON.getLocalizedString(32064)
        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create(utils.ADDON_NAME, STR_GENERATING_ALL_TV_SHOW_METADATA)
        staged_tv_items = self.dbh.get_content_items(
            status='staged', mediatype='tvshow', order='Show_Title'
        )
        for index, item in enumerate(staged_tv_items):
            percent = 100 * index / len(staged_tv_items)
            progress_dialog.update(percent, line2=item.show_title, line3=item.title)
            item.create_metadata_item()
        progress_dialog.close()
        utils.notification(STR_ALL_TV_SHOW_METADATA_CREATED)

    @utils.logged_function
    def read_all_metadata(self):
        ''' Read metadata for all staged tvshow items '''
        STR_READING_ALL_TV_SHOW_METADATA = utils.ADDON.getLocalizedString(32145)
        STR_ALL_TV_SHOW_METADATA_READ = utils.ADDON.getLocalizedString(32146)
        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create(utils.ADDON_NAME, STR_READING_ALL_TV_SHOW_METADATA)
        staged_tv_items = self.dbh.get_content_items(
            status='staged', mediatype='tvshow', order='Show_Title'
        )
        for index, item in enumerate(staged_tv_items):
            percent = 100 * index / len(staged_tv_items)
            progress_dialog.update(percent, line2=item.show_title, line3=item.title)
            item.read_metadata_item()
        progress_dialog.close()
        utils.notification(STR_ALL_TV_SHOW_METADATA_READ)

    @utils.logged_function
    def remove_all(self):
        ''' Remove all staged tvshow items '''
        STR_REMOVING_ALL_TV_SHOWS = utils.ADDON.getLocalizedString(32024)
        STR_ALL_TV_SHOW_REMOVED = utils.ADDON.getLocalizedString(32025)
        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create(utils.ADDON_NAME, STR_REMOVING_ALL_TV_SHOWS)
        self.dbh.remove_all_content_items('staged', 'tvshow')
        progress_dialog.close()
        utils.notification(STR_ALL_TV_SHOW_REMOVED)

    @utils.logged_function
    def remove_all_episodes(self, show_title):
        ''' Remove all episodes from the specified show '''
        STR_REMOVING_ALL_x_EPISODES = utils.ADDON.getLocalizedString(32032) % show_title
        STR_ALL_x_EPISODES_REMOVED = utils.ADDON.getLocalizedString(32033) % show_title
        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create(utils.ADDON_NAME, STR_REMOVING_ALL_x_EPISODES)
        self.dbh.remove_all_show_episodes('staged', show_title)
        progress_dialog.close()
        utils.notification(STR_ALL_x_EPISODES_REMOVED)

    @utils.logged_function
    def remove_and_block_show(self, show_title):
        ''' Remove all episodes from specified show from the library,
        delete metadata, and add to blocked list '''
        # Remove from staged
        self.remove_all_episodes(show_title)
        # Delete metadata folder
        clean_show_title = utils.clean_name(show_title)
        metadata_dir = os.path.join(utils.METADATA_FOLDER, 'TV', clean_show_title)
        utils.fs.remove_dir(metadata_dir)
        # Add show title to blocked
        self.dbh.add_blocked_item(show_title, 'tvshow')

    @utils.logged_function
    def view_episodes(self, show_title):
        ''' Display all staged episodes in the specified show,
        which are selectable and lead to options.
        Also provides additional options at bottom of menu '''
        STR_NO_STAGED_x_EPISODES = utils.ADDON.getLocalizedString(32065) % show_title
        STR_ADD_ALL_EPISODES = utils.ADDON.getLocalizedString(32066)
        STR_ADD_ALL_EPISODES_WITH_METADATA = utils.ADDON.getLocalizedString(32067)
        STR_REMOVE_ALL_EPISODES = utils.ADDON.getLocalizedString(32029)
        STR_REMOVE_AND_BLOCK_TV_SHOW = utils.ADDON.getLocalizedString(32068)
        STR_AUTOMATICALLY_RENAME_ALL_EPISODES_USING_METADATA = utils.ADDON.getLocalizedString(32069)
        STR_GENERATE_ALL_METADATA_ITEMS = utils.ADDON.getLocalizedString(32040)
        STR_BACK = utils.ADDON.getLocalizedString(32011)
        STR_STAGED_x_EPISODES = utils.ADDON.getLocalizedString(32070) % show_title
        staged_episodes = self.dbh.get_content_items(
            status='staged', show_title=show_title, order='Title'
        )
        if not staged_episodes:
            xbmcgui.Dialog().ok(utils.ADDON_NAME, STR_NO_STAGED_x_EPISODES)
            self.view_shows()
            return
        lines = [str(x) for x in staged_episodes]
        lines += [
            STR_ADD_ALL_EPISODES, STR_ADD_ALL_EPISODES_WITH_METADATA, STR_REMOVE_ALL_EPISODES,
            STR_REMOVE_AND_BLOCK_TV_SHOW, STR_AUTOMATICALLY_RENAME_ALL_EPISODES_USING_METADATA,
            STR_GENERATE_ALL_METADATA_ITEMS, STR_BACK
        ]
        ret = xbmcgui.Dialog().select(
            '{0} - {1}'.format(utils.ADDON_NAME, STR_STAGED_x_EPISODES), lines
        )
        if ret >= 0:
            if ret < len(staged_episodes):  # staged item
                for i, item in enumerate(staged_episodes):
                    if ret == i:
                        self.episode_options(item)
                        break
            elif lines[ret] == STR_ADD_ALL_EPISODES:
                self.add_all_episodes(staged_episodes)
                self.view_shows()
            elif lines[ret] == STR_ADD_ALL_EPISODES_WITH_METADATA:
                self.add_all_episodes_with_metadata(staged_episodes)
                self.view_episodes(show_title)
            elif lines[ret] == STR_REMOVE_ALL_EPISODES:
                self.remove_all_episodes(show_title)
                self.view_shows()
            elif lines[ret] == STR_REMOVE_AND_BLOCK_TV_SHOW:
                self.remove_and_block_show(show_title)
                self.view_shows()
            elif lines[ret] == STR_AUTOMATICALLY_RENAME_ALL_EPISODES_USING_METADATA:
                self.rename_episodes_using_metadata(staged_episodes)
                self.view_episodes(show_title)
            elif lines[ret] == STR_GENERATE_ALL_METADATA_ITEMS:
                self.generate_all_episodes_metadata(staged_episodes)
                self.view_episodes(show_title)
            elif lines[ret] == STR_BACK:
                self.view_shows()
        else:
            self.view_shows()

    @utils.logged_function
    def view_shows(self):
        ''' Display all managed tvshows, which are selectable and lead to options.
        Also provides additional options at bottom of menu '''
        STR_NO_STAGED_TV_SHOWS = utils.ADDON.getLocalizedString(32054)
        STR_ADD_ALL_TV_SHOWS = utils.ADDON.getLocalizedString(32055)
        STR_ADD_ALL_ITEMS_WITH_METADTA = utils.ADDON.getLocalizedString(32056)
        STR_REMOVE_ALL_TV_SHOWS = utils.ADDON.getLocalizedString(32057)
        STR_GENERATE_ALL_METADATA_ITEMS = utils.ADDON.getLocalizedString(32040)
        STR_READ_ALL_METADATA_ITEMS = utils.ADDON.getLocalizedString(32147)
        STR_BACK = utils.ADDON.getLocalizedString(32011)
        STR_STAGED_TV_SHOWS = utils.ADDON.getLocalizedString(32058)
        staged_tvshows = self.dbh.get_all_shows('staged')
        if not staged_tvshows:
            xbmcgui.Dialog().ok(utils.ADDON_NAME, STR_NO_STAGED_TV_SHOWS)
            return
        lines = ['[B]{}[/B]'.format(x) for x in staged_tvshows]
        lines += [
            STR_ADD_ALL_TV_SHOWS, STR_ADD_ALL_ITEMS_WITH_METADTA, STR_REMOVE_ALL_TV_SHOWS,
            STR_GENERATE_ALL_METADATA_ITEMS, STR_READ_ALL_METADATA_ITEMS, STR_BACK
        ]
        ret = xbmcgui.Dialog().select(
            '{0} - {1}'.format(utils.ADDON_NAME, STR_STAGED_TV_SHOWS), lines
        )
        if ret >= 0:
            if ret < len(staged_tvshows):  # staged item
                for show_title in staged_tvshows:
                    if staged_tvshows[ret] == show_title:
                        self.view_episodes(show_title)
                        break
            elif lines[ret] == STR_ADD_ALL_TV_SHOWS:
                self.add_all_shows()
            elif lines[ret] == STR_ADD_ALL_ITEMS_WITH_METADTA:
                self.add_all_with_metadata()
                self.view_shows()
            elif lines[ret] == STR_REMOVE_ALL_TV_SHOWS:
                self.remove_all()
            elif lines[ret] == STR_GENERATE_ALL_METADATA_ITEMS:
                self.generate_all_metadata()
                self.view_shows()
            elif lines[ret] == STR_READ_ALL_METADATA_ITEMS:
                self.read_all_metadata()
                self.view_shows()
            elif lines[ret] == STR_BACK:
                return
