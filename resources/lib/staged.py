#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
This module contains the classes StagedMovies and StagedTV,
which provide dialog windows and tools for editing staged movies and tvshow items
'''

import os
import xbmc
import xbmcgui
import xbmcaddon

from utils import get_items, append_item, clean, log_msg

# define managed folder for use throughout code
MANAGED_FOLDER = xbmcaddon.Addon().getSetting('managed_folder')
log_msg('managed_folder: %s' % MANAGED_FOLDER)

class StagedMovies(object):
    '''
    provides windows for displaying staged movies,
    and tools for manipulating the objects and managed file
    '''
    #TODO: try to use self.staged_items consistently in this class
    #?TODO: find a way to only use self.staged_movies?

    def __init__(self, mainmenu):
        self.addon = xbmcaddon.Addon()
        self.STR_ADDON_NAME = self.addon.getAddonInfo('name')
        self.mainmenu = mainmenu

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
        staged_items = get_items('staged.pkl')
        staged_movies = [x for x in staged_items if x.get_mediatype() == 'movie']
        if not staged_movies:
            xbmcgui.Dialog().ok(self.STR_ADDON_NAME, STR_NO_STAGED_MOVIES)
            return self.mainmenu.view()
        lines = [str(x) for x in staged_movies]
        lines, staged_movies = (list(t) for t in zip(*sorted(zip(lines, staged_movies),
                                                             key=lambda x: x[0].lower())))
        lines += [STR_ADD_ALL_MOVIES, STR_ADD_ALL_MOVIES_WITH_METADATA,
                  STR_REMOVE_ALL_MOVIES, STR_GENERATE_ALL_METADATA_ITEMS, STR_BACK]
        ret = xbmcgui.Dialog().select('{0} - {1}'.format(
            self.STR_ADDON_NAME, STR_STAGED_MOVIES), lines)
        if not ret < 0:
            if ret < len(staged_movies):   # staged item
                for i, item in enumerate(staged_movies):
                    if ret == i:
                        return self.options(item)
            elif lines[ret] == STR_ADD_ALL_MOVIES:
                self.add_all()
                return self.mainmenu.view()
            elif lines[ret] == STR_ADD_ALL_MOVIES_WITH_METADATA:
                self.add_all_with_metadata()
                return self.view_all()
            elif lines[ret] == STR_REMOVE_ALL_MOVIES:
                self.remove_all()
                return self.mainmenu.view()
            elif lines[ret] == STR_GENERATE_ALL_METADATA_ITEMS:
                self.generate_all_metadata()
                return self.view_all()
            elif lines[ret] == STR_BACK:
                return self.mainmenu.view()
        else:
            return self.mainmenu.view()

    def add_all(self):
        ''' adds all staged movies to library '''
        STR_ADDING_ALL_MOVIES = self.addon.getLocalizedString(32042)
        STR_ALL_MOVIES_ADDED = self.addon.getLocalizedString(32043)
        pDialog = xbmcgui.DialogProgress()
        pDialog.create(self.STR_ADDON_NAME, STR_ADDING_ALL_MOVIES)
        staged_items = get_items('staged.pkl')
        for item in staged_items:
            if item.get_mediatype() == 'movie':
                pDialog.update(0, line2=item.get_title())
                item.add_to_library()
            else:
                pDialog.update(0, line2=' ')
        pDialog.close()
        xbmc.executebuiltin(
            'Notification("{0}", "{1}")'.format(
                self.STR_ADDON_NAME, STR_ALL_MOVIES_ADDED))

    def add_all_with_metadata(self):
        ''' adds all movies with nfo files to the library '''
        STR_ADDING_ALL_MOVIES_WITH_METADATA = self.addon.getLocalizedString(32044)
        STR_ALL_MOVIES_WITH_METADTA_ADDED = self.addon.getLocalizedString(32045)
        pDialog = xbmcgui.DialogProgress()
        pDialog.create(self.STR_ADDON_NAME, STR_ADDING_ALL_MOVIES_WITH_METADATA)
        staged_items = get_items('staged.pkl')
        for item in staged_items:
            if item.get_mediatype() == 'movie':
                safe_title = clean(item.get_title())
                metadata_dir = os.path.join(MANAGED_FOLDER, 'Metadata', 'Movies', safe_title)
                nfo_path = os.path.join(metadata_dir, safe_title + '.nfo')
                if os.path.exists(nfo_path):
                    pDialog.update(0, line2=item.get_title())
                    item.add_to_library()
            pDialog.update(0, line2=' ')
        pDialog.close()
        xbmc.executebuiltin(
            'Notification("{0}", "{1}")'.format(
                self.STR_ADDON_NAME, STR_ALL_MOVIES_WITH_METADTA_ADDED))

    def remove_all(self):
        ''' removes all staged movies '''
        STR_REMOVING_ALL_MOVIES = self.addon.getLocalizedString(32013)
        STR_ALL_MOVIES_REMOVED = self.addon.getLocalizedString(32014)
        pDialog = xbmcgui.DialogProgress()
        pDialog.create(self.STR_ADDON_NAME, STR_REMOVING_ALL_MOVIES)
        staged_items = get_items('staged.pkl')
        for item in staged_items:
            if item.get_mediatype() == 'movie':
                pDialog.update(0, line2=item.get_title())
                item.remove_from_staged()
            else:
                pDialog.update(0, line2=' ')
        pDialog.close()
        xbmc.executebuiltin(
            'Notification("{0}", "{1}")'.format(
                self.STR_ADDON_NAME, STR_ALL_MOVIES_REMOVED))

    def generate_all_metadata(self):
        ''' generates metadata items for all staged movies '''
        STR_GENERATING_ALL_MOVIE_METADATA = self.addon.getLocalizedString(32046)
        STR_ALL_MOVIE_METADTA_CREATED = self.addon.getLocalizedString(32047)
        pDialog = xbmcgui.DialogProgress()
        pDialog.create(self.STR_ADDON_NAME, STR_GENERATING_ALL_MOVIE_METADATA)
        staged_items = get_items('staged.pkl')
        for item in staged_items:
            if item.get_mediatype() == 'movie':
                pDialog.update(0, line2=item.get_title())
                item.create_metadata_item()
            else:
                pDialog.update(0, line2=' ')
        pDialog.close()
        xbmc.executebuiltin(
            'Notification("{0}", "{1}")'.format(
                self.STR_ADDON_NAME, STR_ALL_MOVIE_METADTA_CREATED))

    def options(self, item):
        ''' provides options for a single staged movie in a dialog window '''
        STR_ADD = self.addon.getLocalizedString(32048)
        STR_REMOVE = self.addon.getLocalizedString(32017)
        STR_REMOVE_AND_BLOCK = self.addon.getLocalizedString(32049)
        STR_RENAME = self.addon.getLocalizedString(32050)
        STR_AUTOMATICALLY_RENAME_USING_METADTA = self.addon.getLocalizedString(32051)
        STR_GENERATE_METADTA_ITEM = self.addon.getLocalizedString(32052)
        STR_STAGED_MOVIE_OPTIONS = self.addon.getLocalizedString(32053)
        lines = [STR_ADD, STR_REMOVE, STR_REMOVE_AND_BLOCK, STR_RENAME,
                 STR_AUTOMATICALLY_RENAME_USING_METADTA, STR_GENERATE_METADTA_ITEM]
        ret = xbmcgui.Dialog().select('{0} - {1} - {2}'.format(
            self.STR_ADDON_NAME, STR_STAGED_MOVIE_OPTIONS, item.get_title()), lines)
        if not ret < 0:
            if lines[ret] == STR_ADD:
                item.add_to_library()
                return self.view_all()
            elif lines[ret] == STR_REMOVE:
                item.remove_from_staged()
                return self.view_all()
            elif lines[ret] == STR_REMOVE_AND_BLOCK:
                item.remove_and_block()
                return self.view_all()
            elif lines[ret] == STR_RENAME:
                self.rename_dialog(item)
                return self.options(item)
            elif lines[ret] == STR_GENERATE_METADTA_ITEM:
                item.create_metadata_item()
                return self.options(item)
            elif lines[ret] == STR_AUTOMATICALLY_RENAME_USING_METADTA:
                item.rename_using_metadata()
                return self.options(item)
        else:
            self.view_all()

    @staticmethod
    def rename_dialog(item):
        ''' prompts input for new name, and renames if non-empty string '''
        #TODO: move to utils so it's not duplicated
        input_ret = xbmcgui.Dialog().input("Title", defaultt=item.title)
        if input_ret:
            item.rename(input_ret)

class StagedTV(object):
    '''
    provides windows for displaying staged tvshows and episodes,
    and tools for manipulating the objects and managed file
    '''

    def __init__(self, mainmenu):
        self.addon = xbmcaddon.Addon()
        self.STR_ADDON_NAME = self.addon.getAddonInfo('name')
        self.mainmenu = mainmenu

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
        staged_items = get_items('staged.pkl')
        staged_tvshows = [x.get_show_title() for x in staged_items if x.get_mediatype() == 'tvshow']
        if not staged_tvshows:
            xbmcgui.Dialog().ok(self.STR_ADDON_NAME, STR_NO_STAGED_TV_SHOWS)
            return self.mainmenu.view()
        staged_tvshows = sorted(list(set(staged_tvshows)), key=str.lower)
        lines = ['[B]%s[/B]' % x for x in staged_tvshows]
        lines += [STR_ADD_ALL_TV_SHOWS, STR_ADD_ALL_ITEMS_WITH_METADTA,
                  STR_REMOVE_ALL_TV_SHOWS, STR_GENERATE_ALL_METADATA_ITEMS, STR_BACK]
        ret = xbmcgui.Dialog().select('{0} - {1}'.format(
            self.STR_ADDON_NAME, STR_STAGED_TV_SHOWS), lines)
        if not ret < 0:
            if ret < len(staged_tvshows):   # staged item
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
        else:
            return self.mainmenu.view()

    def add_all_shows(self):
        ''' adds all tvshow items to library '''
        STR_ADDING_ALL_TV_SHOWS = self.addon.getLocalizedString(32059)
        STR_ALL_TV_SHOWS_ADDED = self.addon.getLocalizedString(32060)
        pDialog = xbmcgui.DialogProgress()
        pDialog.create(self.STR_ADDON_NAME, STR_ADDING_ALL_TV_SHOWS)
        staged_items = get_items('staged.pkl')
        for item in staged_items:
            if item.get_mediatype() == 'tvshow':
                pDialog.update(0, line2=item.get_title())
                item.add_to_library()
            else:
                pDialog.update(0, line2=' ')
        pDialog.close()
        xbmc.executebuiltin(
            'Notification("{0}", "{1}")'.format(
                self.STR_ADDON_NAME, STR_ALL_TV_SHOWS_ADDED))

    def add_all_with_metadata(self):
        ''' adds all tvshow items with nfo file to library'''
        STR_ADDING_ALL_TV_SHOW_ITEMS_WITH_METADATA = self.addon.getLocalizedString(32061)
        STR_ALL_TV_SHOW_ITEMS_WITH_METADATA_ADDED = self.addon.getLocalizedString(32062)
        pDialog = xbmcgui.DialogProgress()
        pDialog.create(self.STR_ADDON_NAME, STR_ADDING_ALL_TV_SHOW_ITEMS_WITH_METADATA)
        staged_items = get_items('staged.pkl')
        for item in staged_items:
            if item.get_mediatype() == 'tvshow':
                safe_title = clean(item.get_title())
                safe_showtitle = clean(item.get_show_title())
                metadata_dir = os.path.join(MANAGED_FOLDER, 'Metadata', 'TV', safe_showtitle)
                nfo_path = os.path.join(metadata_dir, safe_title + '.nfo')
                if os.path.exists(nfo_path):
                    pDialog.update(0, line2=item.get_show_title(), line3=item.get_title())
                    item.add_to_library()
            pDialog.update(0, line2=' ', line3=' ')
        pDialog.close()
        xbmc.executebuiltin(
            'Notification("{0}", "{1}")'.format(
                self.STR_ADDON_NAME, STR_ALL_TV_SHOW_ITEMS_WITH_METADATA_ADDED))

    def remove_all(self):
        ''' removes all staged tvshow items '''
        STR_REMOVING_ALL_TV_SHOWS = self.addon.getLocalizedString(32024)
        STR_ALL_TV_SHOW_REMOVED = self.addon.getLocalizedString(32025)
        pDialog = xbmcgui.DialogProgress()
        pDialog.create(self.STR_ADDON_NAME, STR_REMOVING_ALL_TV_SHOWS)
        staged_items = get_items('staged.pkl')
        for item in staged_items:
            if item.get_mediatype() == 'tvshow':
                pDialog.update(0, line2=item.get_title())
                item.remove_from_staged()
            else:
                pDialog.update(0, line2=' ')
        pDialog.close()
        xbmc.executebuiltin(
            'Notification("{0}", "{1}")'.format(
                self.STR_ADDON_NAME, STR_ALL_TV_SHOW_REMOVED))

    def generate_all_metadata(self):
        ''' creates metadata for all staged tvshow items '''
        STR_GENERATING_ALL_TV_SHOW_METADATA = self.addon.getLocalizedString(32063)
        STR_ALL_TV_SHOW_METADATA_CREATED = self.addon.getLocalizedString(32064)
        pDialog = xbmcgui.DialogProgress()
        pDialog.create(self.STR_ADDON_NAME, STR_GENERATING_ALL_TV_SHOW_METADATA)
        staged_items = get_items('staged.pkl')
        for item in staged_items:
            if item.get_mediatype() == 'tvshow':
                pDialog.update(0, line2=item.get_show_title(), line3=item.get_title())
                item.create_metadata_item()
            else:
                pDialog.update(0, line2=' ', line3=' ')
        pDialog.close()
        xbmc.executebuiltin(
            'Notification("{0}", "{1}")'.format(
                self.STR_ADDON_NAME, STR_ALL_TV_SHOW_METADATA_CREATED))

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
        staged_items = get_items('staged.pkl')
        staged_episodes = [x for x in staged_items \
            if x.get_mediatype() == 'tvshow' and x.get_show_title() == show_title]
        if not staged_episodes:
            xbmcgui.Dialog().ok(self.STR_ADDON_NAME, STR_NO_STAGED_x_EPISODES)
            return self.view_shows()
        lines = [str(x) for x in staged_episodes]
        lines, staged_episodes = (list(t) for t in zip(*sorted(zip(lines, staged_episodes),
                                                               key=lambda x: x[0].lower())))
        lines += [STR_ADD_ALL_EPISODES, STR_ADD_ALL_EPISODES_WITH_METADATA,
                  STR_REMOVE_ALL_EPISODES, STR_REMOVE_AND_BLOCK_TV_SHOW,
                  STR_AUTOMATICALLY_RENAME_ALL_EPISODES_USING_METADATA,
                  STR_GENERATE_ALL_METADATA_ITEMS, STR_BACK]
        ret = xbmcgui.Dialog().select('{0} - {1}'.format(
            self.STR_ADDON_NAME, STR_STAGED_x_EPISODES), lines)
        if not ret < 0:
            if ret < len(staged_episodes):   # staged item
                for i, item in enumerate(staged_episodes):
                    if ret == i:
                        return self.episode_options(item)
            elif lines[ret] == STR_ADD_ALL_EPISODES:
                self.add_all_episodes(show_title)
                return self.view_shows()
            elif lines[ret] == STR_ADD_ALL_EPISODES_WITH_METADATA:
                self.add_all_episodes_with_metadata(show_title)
                return self.view_episodes(show_title)
            elif lines[ret] == STR_REMOVE_ALL_EPISODES:
                self.remove_all_episodes(show_title)
                return self.view_shows()
            elif lines[ret] == STR_REMOVE_AND_BLOCK_TV_SHOW:
                self.remove_and_block_show(show_title)
                return self.view_shows()
            elif lines[ret] == STR_AUTOMATICALLY_RENAME_ALL_EPISODES_USING_METADATA:
                self.rename_episodes_using_metadata(show_title)
                return self.view_episodes(show_title)
            elif lines[ret] == STR_GENERATE_ALL_METADATA_ITEMS:
                self.generate_all_episodes_metadata(show_title)
                return self.view_episodes(show_title)
            elif lines[ret] == STR_BACK:
                return self.view_shows()
        else:
            return self.view_shows()

    def add_all_episodes(self, show_title):
        ''' adds all episodes from specified show to library '''
        STR_ADDING_ALL_x_EPISODES = self.addon.getLocalizedString(32071) % show_title
        STR_ALL_x_EPISODES_ADDED = self.addon.getLocalizedString(32072) % show_title
        pDialog = xbmcgui.DialogProgress()
        pDialog.create(self.STR_ADDON_NAME, STR_ADDING_ALL_x_EPISODES)
        staged_items = get_items('staged.pkl')
        for item in staged_items:
            if item.get_mediatype() == 'tvshow' and item.get_show_title() == show_title:
                pDialog.update(0, line2=item.get_title())
                item.add_to_library()
            else:
                pDialog.update(0, line2=' ')
        pDialog.close()
        xbmc.executebuiltin(
            'Notification("{0}", "{1}")'.format(
                self.STR_ADDON_NAME, STR_ALL_x_EPISODES_ADDED))

    def add_all_episodes_with_metadata(self, show_title):
        ''' adds all episodes in the specified show with metadata to the library '''
        STR_ADDING_ALL_x_EPISODES_WITH_METADATA = self.addon.getLocalizedString(32073) % show_title
        STR_ALL_x_EPISODES_WITH_METADATA_ADDED = self.addon.getLocalizedString(32074) % show_title
        pDialog = xbmcgui.DialogProgress()
        pDialog.create(self.STR_ADDON_NAME, STR_ADDING_ALL_x_EPISODES_WITH_METADATA)
        staged_items = get_items('staged.pkl')
        for item in staged_items:
            if item.get_mediatype() == 'tvshow' and item.get_show_title() == show_title:
                safe_title = clean(item.get_title())
                safe_showtitle = clean(show_title)
                metadata_dir = os.path.join(MANAGED_FOLDER, 'Metadata', 'TV', safe_showtitle)
                nfo_path = os.path.join(metadata_dir, safe_title + '.nfo')
                if os.path.exists(nfo_path):
                    pDialog.update(0, line2=show_title, line3=item.get_title())
                    item.add_to_library()
            pDialog.update(0, line2=' ', line3=' ')
        pDialog.close()
        xbmc.executebuiltin(
            'Notification("{0}", "{1}")'.format(
                self.STR_ADDON_NAME, STR_ALL_x_EPISODES_WITH_METADATA_ADDED))

    def remove_all_episodes(self, show_title):
        ''' removes all episodes from the specified show '''
        STR_REMOVING_ALL_x_EPISODES = self.addon.getLocalizedString(32032) % show_title
        STR_ALL_x_EPISODES_REMOVED = self.addon.getLocalizedString(32033) % show_title
        pDialog = xbmcgui.DialogProgress()
        pDialog.create(self.STR_ADDON_NAME, STR_REMOVING_ALL_x_EPISODES)
        staged_items = get_items('staged.pkl')
        for item in staged_items:
            if item.get_mediatype() == 'tvshow' and item.get_show_title() == show_title:
                pDialog.update(0, line2=item.get_title())
                item.remove_from_staged()
            else:
                pDialog.update(0, line2=' ')
        pDialog.close()
        xbmc.executebuiltin(
            'Notification("{0}", "{1}")'.format(
                self.STR_ADDON_NAME, STR_ALL_x_EPISODES_REMOVED))

    def remove_and_block_show(self, show_title):
        '''
        removes all episodes from specified show from the library,
        deletes metadata, and adds to blocked list
        '''
        # remove from staged
        self.remove_all_episodes(show_title)
        # delete metadata folder
        safe_showtitle = clean(show_title)
        metadata_dir = os.path.join(MANAGED_FOLDER, 'Metadata', 'TV', safe_showtitle)
        os.system('rm -r "%s"' % metadata_dir)
        # add show title to blocked
        append_item('blocked.pkl', {'type':'tvshow', 'label':show_title})

    def rename_episodes_using_metadata(self, show_title):
        ''' automatically renames all episodes in show using nfo files '''
        STR_RENAMING_x_EPISODES_USING_METADATA = self.addon.getLocalizedString(32075) % show_title
        STR_x_EPISODES_RENAMED_USING_METADATA = self.addon.getLocalizedString(32076) % show_title
        pDialog = xbmcgui.DialogProgress()
        pDialog.create(self.STR_ADDON_NAME, STR_RENAMING_x_EPISODES_USING_METADATA)
        staged_items = get_items('staged.pkl')
        for item in staged_items:
            if item.get_mediatype() == 'tvshow' and item.get_show_title() == show_title:
                pDialog.update(0, line2=item.get_title())
                item.rename_using_metadata()
            else:
                pDialog.update(0, line2=' ')
        pDialog.close()
        xbmc.executebuiltin(
            'Notification("{0}", "{1}")'.format(
                self.STR_ADDON_NAME, STR_x_EPISODES_RENAMED_USING_METADATA))

    def generate_all_episodes_metadata(self, show_title):
        ''' generates metadata items for all episodes in show '''
        STR_GENERATING_ALL_x_METADATA = self.addon.getLocalizedString(32077) % show_title
        STR_ALL_x_METADATA_CREATED = self.addon.getLocalizedString(32078) % show_title
        pDialog = xbmcgui.DialogProgress()
        pDialog.create(self.STR_ADDON_NAME, STR_GENERATING_ALL_x_METADATA)
        staged_items = get_items('staged.pkl')
        for item in staged_items:
            if item.get_mediatype() == 'tvshow' and item.get_show_title() == show_title:
                pDialog.update(0, line2=item.get_title())
                item.create_metadata_item()
            else:
                pDialog.update(0, line2=' ')
        pDialog.close()
        xbmc.executebuiltin(
            'Notification("{0}", {1}")'.format(
                self.STR_ADDON_NAME, STR_ALL_x_METADATA_CREATED))

    def episode_options(self, item):
        ''' provides options for a single staged episode in a dialog window '''
        #TODO: rename associated metadata when renaming
        #TODO: change item.show_title to item.get_show_title after I've rebuilt library
        #TODO: automatically rename based on nfo file for all items in tv show
        #TODO: rename show title
        #TODO: add to blocked movies/shows
        #TODO: remove item (including metadata)
        STR_ADD = self.addon.getLocalizedString(32048)
        STR_REMOVE = self.addon.getLocalizedString(32017)
        STR_REMOVE_AND_BLOCK_EPISODE = self.addon.getLocalizedString(32079)
        STR_RENAME = self.addon.getLocalizedString(32050)
        STR_AUTOMATICALLY_RENAME_USING_METADTA = self.addon.getLocalizedString(32051)
        STR_GENERATE_METADTA_ITEM = self.addon.getLocalizedString(32052)
        STR_BACK = self.addon.getLocalizedString(32011)
        STR_STAGED_EPISODE_OPTIONS = self.addon.getLocalizedString(32080)
        lines = [STR_ADD, STR_REMOVE, STR_REMOVE_AND_BLOCK_EPISODE, STR_RENAME,
                 STR_AUTOMATICALLY_RENAME_USING_METADTA, STR_GENERATE_METADTA_ITEM, STR_BACK]
        ret = xbmcgui.Dialog().select('{0} - {1} - {2}'.format(
            self.STR_ADDON_NAME, STR_STAGED_EPISODE_OPTIONS, item.get_title()), lines)
        if not ret < 0:
            if lines[ret] == STR_ADD:
                item.add_to_library()
                return self.view_episodes(item.get_show_title())
            elif lines[ret] == STR_REMOVE:
                item.remove_from_staged()
                return self.view_episodes(item.get_show_title())
            elif lines[ret] == STR_REMOVE_AND_BLOCK_EPISODE:
                item.remove_and_block()
                return self.view_episodes(item.get_show_title())
            elif lines[ret] == STR_RENAME:
                self.rename_dialog(item)
                return self.episode_options(item)
            elif lines[ret] == STR_GENERATE_METADTA_ITEM:
                item.create_metadata_item()
                return self.episode_options(item)
            elif lines[ret] == STR_AUTOMATICALLY_RENAME_USING_METADTA:
                item.rename_using_metadata()
                return self.episode_options(item)
            elif lines[ret] == STR_BACK:
                return self.view_episodes(item.get_show_title())
        else:
            return self.view_episodes(item.get_show_title())

    @staticmethod
    def rename_dialog(item):
        ''' prompts input for new name, and renames if non-empty string '''
        input_ret = xbmcgui.Dialog().input("Title", defaultt=item.title)
        if input_ret:
            item.rename(input_ret)
