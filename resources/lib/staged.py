#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
This module contains the classes StagedMovies and StagedTV,
which provide dialog windows and tools for editing staged movies and tvshow items
'''

import shutil
import os
import xbmc
import xbmcgui
import xbmcaddon
from glob import glob

from .database_handler import DB_Handler
from .utils import clean_name, log_decorator, log_msg, notification

# get tools depending on platform
if os.name == 'posix':
    import unix as fs
else:
    import universal as fs

# define managed folder for use throughout code
MANAGED_FOLDER = xbmcaddon.Addon().getSetting('managed_folder')


class StagedMovies(object):
    '''
    provides windows for displaying staged movies,
    and tools for manipulating the objects and managed file
    '''

    #TODO: don't commit sql changes for "... all" until end
    #TODO: decorator for "...all" commands
    #TODO: load staged movies on init, use as class variable, refresh as needed

    def __init__(self, mainmenu):
        self.addon = xbmcaddon.Addon()
        self.STR_ADDON_NAME = self.addon.getAddonInfo('name')
        self.mainmenu = mainmenu
        self.dbh = DB_Handler()

    @log_decorator
    def add_all(self, items):
        ''' adds all staged movies to library '''
        STR_ADDING_ALL_MOVIES = self.addon.getLocalizedString(32042)
        STR_ALL_MOVIES_ADDED = self.addon.getLocalizedString(32043)
        pDialog = xbmcgui.DialogProgress()
        pDialog.create(self.STR_ADDON_NAME, STR_ADDING_ALL_MOVIES)
        for item in items:
            pDialog.update(0, line2=item.get_title())
            item.add_to_library()
        pDialog.close()
        notification(STR_ALL_MOVIES_ADDED)

    @log_decorator
    def add_all_with_metadata(self, items):
        ''' adds all movies with nfo files to the library '''
        STR_ADDING_ALL_MOVIES_WITH_METADATA = self.addon.getLocalizedString(32044)
        STR_ALL_MOVIES_WITH_METADTA_ADDED = self.addon.getLocalizedString(32045)
        pDialog = xbmcgui.DialogProgress()
        pDialog.create(self.STR_ADDON_NAME, STR_ADDING_ALL_MOVIES_WITH_METADATA)
        for item in items:
            safe_title = clean_name(item.get_title())
            metadata_dir = os.path.join(MANAGED_FOLDER, 'Metadata', 'Movies', safe_title)
            nfo_path = os.path.join(metadata_dir, safe_title + '.nfo')
            if os.path.exists(nfo_path):
                pDialog.update(0, line2=item.get_title())
                item.add_to_library()
            pDialog.update(0, line2=' ')
        pDialog.close()
        notification(STR_ALL_MOVIES_WITH_METADTA_ADDED)

    @log_decorator
    def generate_all_metadata(self, items):
        ''' Generates metadata items for all staged movies '''
        STR_GENERATING_ALL_MOVIE_METADATA = self.addon.getLocalizedString(32046)
        STR_ALL_MOVIE_METADTA_CREATED = self.addon.getLocalizedString(32047)
        pDialog = xbmcgui.DialogProgress()
        pDialog.create(self.STR_ADDON_NAME, STR_GENERATING_ALL_MOVIE_METADATA)
        for item in items:
            pDialog.update(0, line2=item.get_title())
            item.create_metadata_item()
        pDialog.close()
        notification(STR_ALL_MOVIE_METADTA_CREATED)

    @log_decorator
    def options(self, item):
        ''' Provides options for a single staged movie in a dialog window '''
        #TODO: add a back button
        STR_ADD = self.addon.getLocalizedString(32048)
        STR_REMOVE = self.addon.getLocalizedString(32017)
        STR_REMOVE_AND_BLOCK = self.addon.getLocalizedString(32049)
        STR_RENAME = self.addon.getLocalizedString(32050)
        STR_AUTOMATICALLY_RENAME_USING_METADTA = self.addon.getLocalizedString(32051)
        STR_GENERATE_METADATA_ITEM = self.addon.getLocalizedString(32052)
        STR_STAGED_MOVIE_OPTIONS = self.addon.getLocalizedString(32053)
        lines = [
            STR_ADD,
            STR_REMOVE,
            STR_REMOVE_AND_BLOCK,
            #STR_RENAME, STR_AUTOMATICALLY_RENAME_USING_METADTA,
            STR_GENERATE_METADATA_ITEM
        ]
        ret = xbmcgui.Dialog().select(
            '{0} - {1} - {2}'.format(self.STR_ADDON_NAME, STR_STAGED_MOVIE_OPTIONS,
                                     item.get_title()), lines)
        if ret >= 0:
            if lines[ret] == STR_ADD:
                item.add_to_library()
                return self.view_all()
            elif lines[ret] == STR_REMOVE:
                item.delete()
                return self.view_all()
            elif lines[ret] == STR_REMOVE_AND_BLOCK:
                item.remove_and_block()
                return self.view_all()
            elif lines[ret] == STR_RENAME:
                self.rename_dialog(item)
                return self.options(item)
            elif lines[ret] == STR_GENERATE_METADATA_ITEM:
                item.create_metadata_item()
                return self.options(item)
            elif lines[ret] == STR_AUTOMATICALLY_RENAME_USING_METADTA:
                item.rename_using_metadata()
                return self.options(item)
        self.view_all()

    @log_decorator
    def remove_all(self):
        ''' removes all staged movies '''
        STR_REMOVING_ALL_MOVIES = self.addon.getLocalizedString(32013)
        STR_ALL_MOVIES_REMOVED = self.addon.getLocalizedString(32014)
        pDialog = xbmcgui.DialogProgress()
        pDialog.create(self.STR_ADDON_NAME, STR_REMOVING_ALL_MOVIES)
        self.dbh.remove_all_content_items('staged', 'movie')
        pDialog.close()
        notification(STR_ALL_MOVIES_REMOVED)

    @log_decorator
    def remove_stale_metadata(self):
        ''' Removes all unused metadata '''
        STR_STALE_METADATA_REMOVED = self.addon.getLocalizedString(32136)
        metadata_dir = os.path.join(MANAGED_FOLDER, 'Metadata', 'Movies')
        for folder in os.listdir(metadata_dir):
            full_path = os.path.join(metadata_dir, folder)
            if os.path.isdir(full_path) and not glob(os.path.join(full_path, '*.nfo')):
                log_msg('Removing metadata folder {}'.format(full_path), loglevel=xbmc.LOGNOTICE)
                shutil.rmtree(full_path)
        notification(STR_STALE_METADATA_REMOVED)

    @staticmethod
    def rename_dialog(item):
        ''' prompts input for new name, and renames if non-empty string '''
        #TODO: move to utils or parent class so it's not duplicated
        input_ret = xbmcgui.Dialog().input("Title", defaultt=item.title)
        if input_ret:
            item.rename(input_ret)

    @log_decorator
    def view_all(self):
        '''
        displays all staged movies, which are selectable and lead to options.
        also provides additional options at bottom of menu
        '''
        STR_NO_STAGED_MOVIES = self.addon.getLocalizedString(32037)
        STR_ADD_ALL_MOVIES = self.addon.getLocalizedString(32038)
        STR_ADD_ALL_MOVIES_WITH_METADATA = self.addon.getLocalizedString(32039)
        STR_REMOVE_ALL_MOVIES = self.addon.getLocalizedString(32009)
        STR_GENERATE_ALL_METADATA_ITEMS = self.addon.getLocalizedString(32040)
        STR_BACK = self.addon.getLocalizedString(32011)
        STR_STAGED_MOVIES = self.addon.getLocalizedString(32041)
        STR_REMOVE_STALE_METADATA = self.addon.getLocalizedString(32135)
        staged_movies = self.dbh.get_content_items(
            status='staged', mediatype='movie', order='Title')
        if not staged_movies:
            xbmcgui.Dialog().ok(self.STR_ADDON_NAME, STR_NO_STAGED_MOVIES)
            return self.mainmenu.view()
        lines = [str(x) for x in staged_movies]
        lines += [
            STR_ADD_ALL_MOVIES,
            STR_ADD_ALL_MOVIES_WITH_METADATA,
            STR_REMOVE_ALL_MOVIES,
            STR_GENERATE_ALL_METADATA_ITEMS,
            STR_REMOVE_STALE_METADATA,
            STR_BACK
        ]
        ret = xbmcgui.Dialog().select('{0} - {1}'.format(self.STR_ADDON_NAME, STR_STAGED_MOVIES),
                                      lines)
        if not ret < 0:
            if ret < len(staged_movies):  # staged item
                for i, item in enumerate(staged_movies):
                    if ret == i:
                        return self.options(item)
            elif lines[ret] == STR_ADD_ALL_MOVIES:
                self.add_all(staged_movies)
                return self.mainmenu.view()
            elif lines[ret] == STR_ADD_ALL_MOVIES_WITH_METADATA:
                self.add_all_with_metadata(staged_movies)
                return self.view_all()
            elif lines[ret] == STR_REMOVE_ALL_MOVIES:
                self.remove_all()
                return self.mainmenu.view()
            elif lines[ret] == STR_GENERATE_ALL_METADATA_ITEMS:
                self.generate_all_metadata(staged_movies)
                return self.view_all()
            elif lines[ret] == STR_REMOVE_STALE_METADATA:
                self.remove_stale_metadata()
                return self.view_all()
            elif lines[ret] == STR_BACK:
                return self.mainmenu.view()
        return self.mainmenu.view()


class StagedTV(object):
    '''
    provides windows for displaying staged tvshows and episodes,
    and tools for manipulating the objects and managed file
    '''

    def __init__(self, mainmenu):
        self.addon = xbmcaddon.Addon()
        self.STR_ADDON_NAME = self.addon.getAddonInfo('name')
        self.mainmenu = mainmenu
        self.dbh = DB_Handler()

    @log_decorator
    def add_all_episodes(self, items):
        ''' adds all episodes from specified show to library '''
        STR_ADDING_ALL_x_EPISODES = self.addon.getLocalizedString(32071)
        STR_ALL_x_EPISODES_ADDED = self.addon.getLocalizedString(32072)
        show_title = items[0].get_show_title()
        pDialog = xbmcgui.DialogProgress()
        pDialog.create(self.STR_ADDON_NAME, STR_ADDING_ALL_x_EPISODES % show_title)
        for item in items:
            pDialog.update(0, line2=item.get_title())
            item.add_to_library()
        pDialog.close()
        notification(STR_ALL_x_EPISODES_ADDED % show_title)

    @log_decorator
    def add_all_episodes_with_metadata(self, items):
        ''' adds all episodes in the specified show with metadata to the library '''
        STR_ADDING_ALL_x_EPISODES_WITH_METADATA = self.addon.getLocalizedString(32073)
        STR_ALL_x_EPISODES_WITH_METADATA_ADDED = self.addon.getLocalizedString(32074)
        show_title = items[0].get_show_title()
        safe_showtitle = clean_name(show_title)
        metadata_dir = os.path.join(MANAGED_FOLDER, 'Metadata', 'TV', safe_showtitle)
        pDialog = xbmcgui.DialogProgress()
        pDialog.create(self.STR_ADDON_NAME, STR_ADDING_ALL_x_EPISODES_WITH_METADATA % show_title)
        for item in items:
            safe_title = clean_name(item.get_title())
            nfo_path = os.path.join(metadata_dir, safe_title + '.nfo')
            if os.path.exists(nfo_path):
                pDialog.update(0, line2=item.get_title())
                item.add_to_library()
            pDialog.update(0, line2=' ')
        pDialog.close()
        notification(STR_ALL_x_EPISODES_WITH_METADATA_ADDED % show_title)

    @log_decorator
    def add_all_shows(self):
        ''' adds all tvshow items to library '''
        STR_ADDING_ALL_TV_SHOWS = self.addon.getLocalizedString(32059)
        STR_ALL_TV_SHOWS_ADDED = self.addon.getLocalizedString(32060)
        pDialog = xbmcgui.DialogProgress()
        pDialog.create(self.STR_ADDON_NAME, STR_ADDING_ALL_TV_SHOWS)
        staged_tv_items = self.dbh.get_content_items(
            status='staged', mediatype='tvshow', order='Show_Title')
        for item in staged_tv_items:
            pDialog.update(0, line2=item.get_title())
            item.add_to_library()
        pDialog.close()
        notification(STR_ALL_TV_SHOWS_ADDED)

    @log_decorator
    def add_all_with_metadata(self):
        ''' adds all tvshow items with nfo file to library'''
        STR_ADDING_ALL_TV_SHOW_ITEMS_WITH_METADATA = self.addon.getLocalizedString(32061)
        STR_ALL_TV_SHOW_ITEMS_WITH_METADATA_ADDED = self.addon.getLocalizedString(32062)
        pDialog = xbmcgui.DialogProgress()
        pDialog.create(self.STR_ADDON_NAME, STR_ADDING_ALL_TV_SHOW_ITEMS_WITH_METADATA)
        staged_tv_items = self.dbh.get_content_items(
            status='staged', mediatype='tvshow', order='Show_Title')
        for item in staged_tv_items:
            safe_title = clean_name(item.get_title())
            safe_showtitle = clean_name(item.get_show_title())
            metadata_dir = os.path.join(MANAGED_FOLDER, 'Metadata', 'TV', safe_showtitle)
            nfo_path = os.path.join(metadata_dir, safe_title + '.nfo')
            if os.path.exists(nfo_path):
                pDialog.update(0, line2=item.get_show_title(), line3=item.get_title())
                item.add_to_library()
            pDialog.update(0, line2=' ', line3=' ')
        pDialog.close()
        notification(STR_ALL_TV_SHOW_ITEMS_WITH_METADATA_ADDED)

    @log_decorator
    def episode_options(self, item):
        ''' provides options for a single staged episode in a dialog window '''
        #TODO: rename associated metadata when renaming
        #TODO: rename show title
        #TODO: remove item (including metadata)
        STR_ADD = self.addon.getLocalizedString(32048)
        STR_REMOVE = self.addon.getLocalizedString(32017)
        STR_REMOVE_AND_BLOCK_EPISODE = self.addon.getLocalizedString(32079)
        STR_RENAME = self.addon.getLocalizedString(32050)
        STR_AUTOMATICALLY_RENAME_USING_METADTA = self.addon.getLocalizedString(32051)
        STR_GENERATE_METADATA_ITEM = self.addon.getLocalizedString(32052)
        STR_BACK = self.addon.getLocalizedString(32011)
        STR_STAGED_EPISODE_OPTIONS = self.addon.getLocalizedString(32080)
        lines = [
            STR_ADD, STR_REMOVE, STR_REMOVE_AND_BLOCK_EPISODE, STR_RENAME,
            STR_AUTOMATICALLY_RENAME_USING_METADTA, STR_GENERATE_METADATA_ITEM, STR_BACK
        ]
        ret = xbmcgui.Dialog().select(
            '{0} - {1} - {2}'.format(self.STR_ADDON_NAME, STR_STAGED_EPISODE_OPTIONS,
                                     item.get_title()), lines)
        if not ret < 0:
            if lines[ret] == STR_ADD:
                item.add_to_library()
                return self.view_episodes(item.get_show_title())
            elif lines[ret] == STR_REMOVE:
                item.delete()
                return self.view_episodes(item.get_show_title())
            elif lines[ret] == STR_REMOVE_AND_BLOCK_EPISODE:
                item.remove_and_block()
                return self.view_episodes(item.get_show_title())
            elif lines[ret] == STR_RENAME:
                self.rename_dialog(item)
                return self.episode_options(item)
            elif lines[ret] == STR_GENERATE_METADATA_ITEM:
                item.create_metadata_item()
                return self.episode_options(item)
            elif lines[ret] == STR_AUTOMATICALLY_RENAME_USING_METADTA:
                item.rename_using_metadata()
                return self.episode_options(item)
            elif lines[ret] == STR_BACK:
                return self.view_episodes(item.get_show_title())
        return self.view_episodes(item.get_show_title())

    @log_decorator
    def remove_all(self):
        ''' removes all staged tvshow items '''
        STR_REMOVING_ALL_TV_SHOWS = self.addon.getLocalizedString(32024)
        STR_ALL_TV_SHOW_REMOVED = self.addon.getLocalizedString(32025)
        pDialog = xbmcgui.DialogProgress()
        pDialog.create(self.STR_ADDON_NAME, STR_REMOVING_ALL_TV_SHOWS)
        self.dbh.remove_all_content_items('staged', 'tvshow')
        pDialog.close()
        notification(STR_ALL_TV_SHOW_REMOVED)

    @log_decorator
    def generate_all_episodes_metadata(self, items):
        ''' generates metadata items for all episodes in show '''
        STR_GENERATING_ALL_x_METADATA = self.addon.getLocalizedString(32077)
        STR_ALL_x_METADATA_CREATED = self.addon.getLocalizedString(32078)
        show_title = items[0].get_show_title()
        pDialog = xbmcgui.DialogProgress()
        pDialog.create(self.STR_ADDON_NAME, STR_GENERATING_ALL_x_METADATA % show_title)
        for item in items:
            pDialog.update(0, line2=item.get_title())
            item.create_metadata_item()
        pDialog.close()
        notification(STR_ALL_x_METADATA_CREATED % show_title)

    @log_decorator
    def generate_all_metadata(self):
        ''' creates metadata for all staged tvshow items '''
        STR_GENERATING_ALL_TV_SHOW_METADATA = self.addon.getLocalizedString(32063)
        STR_ALL_TV_SHOW_METADATA_CREATED = self.addon.getLocalizedString(32064)
        pDialog = xbmcgui.DialogProgress()
        pDialog.create(self.STR_ADDON_NAME, STR_GENERATING_ALL_TV_SHOW_METADATA)
        staged_tv_items = self.dbh.get_content_items(
            status='staged', mediatype='tvshow', order='Show_Title')
        for item in staged_tv_items:
            pDialog.update(0, line2=item.get_show_title(), line3=item.get_title())
            item.create_metadata_item()
        pDialog.close()
        notification(STR_ALL_TV_SHOW_METADATA_CREATED)

    @log_decorator
    def remove_all_episodes(self, show_title):
        ''' removes all episodes from the specified show '''
        STR_REMOVING_ALL_x_EPISODES = self.addon.getLocalizedString(32032) % show_title
        STR_ALL_x_EPISODES_REMOVED = self.addon.getLocalizedString(32033) % show_title
        pDialog = xbmcgui.DialogProgress()
        pDialog.create(self.STR_ADDON_NAME, STR_REMOVING_ALL_x_EPISODES)
        self.dbh.remove_all_show_episodes('staged', show_title)
        pDialog.close()
        notification(STR_ALL_x_EPISODES_REMOVED)

    @log_decorator
    def remove_and_block_show(self, show_title):
        '''
        removes all episodes from specified show from the library,
        deletes metadata, and adds to blocked list
        '''
        # remove from staged
        self.remove_all_episodes(show_title)
        # delete metadata folder
        safe_showtitle = clean_name(show_title)
        metadata_dir = os.path.join(MANAGED_FOLDER, 'Metadata', 'TV', safe_showtitle)
        fs.remove_dir(metadata_dir)
        # add show title to blocked
        self.dbh.add_blocked_item(show_title, 'tvshow')

    @staticmethod
    def rename_dialog(item):
        ''' prompts input for new name, and renames if non-empty string '''
        input_ret = xbmcgui.Dialog().input("Title", defaultt=item.title)
        if input_ret:
            item.rename(input_ret)

    @log_decorator
    def rename_episodes_using_metadata(self, items):
        ''' automatically renames all episodes in show using nfo files '''
        STR_RENAMING_x_EPISODES_USING_METADATA = self.addon.getLocalizedString(32075)
        STR_x_EPISODES_RENAMED_USING_METADATA = self.addon.getLocalizedString(32076)
        show_title = items[0].get_show_title()
        pDialog = xbmcgui.DialogProgress()
        pDialog.create(self.STR_ADDON_NAME, STR_RENAMING_x_EPISODES_USING_METADATA % show_title)
        for item in items:
            pDialog.update(0, line2=item.get_title())
            item.rename_using_metadata()
        pDialog.close()
        notification(STR_x_EPISODES_RENAMED_USING_METADATA % show_title)

    @log_decorator
    def view_episodes(self, show_title):
        '''
        displays all staged episodes in the specified show,
        which are selectable and lead to options.
        also provides additional options at bottom of menu
        '''
        STR_NO_STAGED_x_EPISODES = self.addon.getLocalizedString(32065) % show_title
        STR_ADD_ALL_EPISODES = self.addon.getLocalizedString(32066)
        STR_ADD_ALL_EPISODES_WITH_METADATA = self.addon.getLocalizedString(32067)
        STR_REMOVE_ALL_EPISODES = self.addon.getLocalizedString(32029)
        STR_REMOVE_AND_BLOCK_TV_SHOW = self.addon.getLocalizedString(32068)
        STR_AUTOMATICALLY_RENAME_ALL_EPISODES_USING_METADATA = self.addon.getLocalizedString(32069)
        STR_GENERATE_ALL_METADATA_ITEMS = self.addon.getLocalizedString(32040)
        STR_BACK = self.addon.getLocalizedString(32011)
        STR_STAGED_x_EPISODES = self.addon.getLocalizedString(32070) % show_title
        staged_episodes = self.dbh.get_content_items(
            status='staged', show_title=show_title, order='Title')
        if not staged_episodes:
            xbmcgui.Dialog().ok(self.STR_ADDON_NAME, STR_NO_STAGED_x_EPISODES)
            return self.view_shows()
        lines = [str(x) for x in staged_episodes]
        lines += [
            STR_ADD_ALL_EPISODES, STR_ADD_ALL_EPISODES_WITH_METADATA, STR_REMOVE_ALL_EPISODES,
            STR_REMOVE_AND_BLOCK_TV_SHOW, STR_AUTOMATICALLY_RENAME_ALL_EPISODES_USING_METADATA,
            STR_GENERATE_ALL_METADATA_ITEMS, STR_BACK
        ]
        ret = xbmcgui.Dialog().select(
            '{0} - {1}'.format(self.STR_ADDON_NAME, STR_STAGED_x_EPISODES), lines)
        if not ret < 0:
            if ret < len(staged_episodes):  # staged item
                for i, item in enumerate(staged_episodes):
                    if ret == i:
                        return self.episode_options(item)
            elif lines[ret] == STR_ADD_ALL_EPISODES:
                self.add_all_episodes(staged_episodes)
                return self.view_shows()
            elif lines[ret] == STR_ADD_ALL_EPISODES_WITH_METADATA:
                self.add_all_episodes_with_metadata(staged_episodes)
                return self.view_episodes(show_title)
            elif lines[ret] == STR_REMOVE_ALL_EPISODES:
                self.remove_all_episodes(show_title)
                return self.view_shows()
            elif lines[ret] == STR_REMOVE_AND_BLOCK_TV_SHOW:
                self.remove_and_block_show(show_title)
                return self.view_shows()
            elif lines[ret] == STR_AUTOMATICALLY_RENAME_ALL_EPISODES_USING_METADATA:
                self.rename_episodes_using_metadata(staged_episodes)
                return self.view_episodes(show_title)
            elif lines[ret] == STR_GENERATE_ALL_METADATA_ITEMS:
                self.generate_all_episodes_metadata(staged_episodes)
                return self.view_episodes(show_title)
            elif lines[ret] == STR_BACK:
                return self.view_shows()
        return self.view_shows()

    @log_decorator
    def view_shows(self):
        '''
        displays all managed tvshows, which are selectable and lead to options.
        also provides additional options at bottom of menu
        '''
        STR_NO_STAGED_TV_SHOWS = self.addon.getLocalizedString(32054)
        STR_ADD_ALL_TV_SHOWS = self.addon.getLocalizedString(32055)
        STR_ADD_ALL_ITEMS_WITH_METADTA = self.addon.getLocalizedString(32056)
        STR_REMOVE_ALL_TV_SHOWS = self.addon.getLocalizedString(32057)
        STR_GENERATE_ALL_METADATA_ITEMS = self.addon.getLocalizedString(32040)
        STR_BACK = self.addon.getLocalizedString(32011)
        STR_STAGED_TV_SHOWS = self.addon.getLocalizedString(32058)
        staged_tvshows = self.dbh.get_all_shows('staged')
        if not staged_tvshows:
            xbmcgui.Dialog().ok(self.STR_ADDON_NAME, STR_NO_STAGED_TV_SHOWS)
            return self.mainmenu.view()
        lines = ['[B]%s[/B]' % x for x in staged_tvshows]
        lines += [
            STR_ADD_ALL_TV_SHOWS, STR_ADD_ALL_ITEMS_WITH_METADTA, STR_REMOVE_ALL_TV_SHOWS,
            STR_GENERATE_ALL_METADATA_ITEMS, STR_BACK
        ]
        ret = xbmcgui.Dialog().select('{0} - {1}'.format(self.STR_ADDON_NAME, STR_STAGED_TV_SHOWS),
                                      lines)
        if not ret < 0:
            if ret < len(staged_tvshows):  # staged item
                for show_title in staged_tvshows:
                    if staged_tvshows[ret] == show_title:
                        return self.view_episodes(show_title)
            elif lines[ret] == STR_ADD_ALL_TV_SHOWS:
                self.add_all_shows()
                return self.mainmenu.view()
            elif lines[ret] == STR_ADD_ALL_ITEMS_WITH_METADTA:
                self.add_all_with_metadata()
                return self.view_shows()
            elif lines[ret] == STR_REMOVE_ALL_TV_SHOWS:
                self.remove_all()
                return self.mainmenu.view()
            elif lines[ret] == STR_GENERATE_ALL_METADATA_ITEMS:
                self.generate_all_metadata()
                return self.view_shows()
            elif lines[ret] == STR_BACK:
                return self.mainmenu.view()
        return self.mainmenu.view()
