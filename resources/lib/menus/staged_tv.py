#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Defines the StagedTVMenu class
'''

import os.path

import xbmc # pylint: disable=import-error
import xbmcgui # pylint: disable=import-error

from resources import ADDON_NAME
from resources.lib.utils import METADATA_FOLDER

from resources.lib.log import logged_function
from resources.lib.filesystem import remove_dir

from resources.lib.utils import clean_name
from resources.lib.utils import notification
from resources.lib.utils import getlocalizedstring

from resources.lib.database_handler import DatabaseHandler


class StagedTVMenu(object):
    ''' Provide windows for displaying staged tvshows and episodes,
    and tools for managing the items '''

    def __init__(self):
        self.dbh = DatabaseHandler()


    @staticmethod
    @logged_function
    def add_all_episodes(items):
        ''' Add all episodes from specified show to library '''
        STR_ADDING_ALL_x_EPISODES = getlocalizedstring(32071)
        STR_ALL_x_EPISODES_ADDED = getlocalizedstring(32072)
        show_title = items[0].show_title

        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create(ADDON_NAME, STR_ADDING_ALL_x_EPISODES % show_title)

        for index, item in enumerate(items):
            percent = 100 * index / len(items)
            progress_dialog.update(int(percent), '\n'.join([item.show_title, item.episode_title_with_id]))
            xbmc.sleep(200)
            item.add_to_library()
        progress_dialog.close()
        notification(STR_ALL_x_EPISODES_ADDED % show_title)


    @logged_function
    def add_all_seasons(self, show_title):
        ''' Add all episodes from specified show to library '''
        STR_ADDING_ALL_x_SEASONS = 'Adding all %s seasons...'
        STR_ALL_x_SEASONS_ADDED = 'All %s seasons added'

        staged_seasons = self.dbh.get_content_items(
            status='staged', mediatype='tvshow', order='Show_Title', show_title=show_title
        )

        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create(ADDON_NAME, STR_ADDING_ALL_x_SEASONS % show_title)

        for index, item in enumerate(staged_seasons):
            percent = 100 * index / len(staged_seasons)
            progress_dialog.update(int(percent), '\n'.join([item.show_title, item.episode_title_with_id]))
            xbmc.sleep(100)
            item.add_to_library()
        progress_dialog.close()
        notification(STR_ALL_x_SEASONS_ADDED % show_title)


    @logged_function
    def add_all_seasons_with_metadata(self, show_title):
        ''' Add all seasons in the specified show with metadata to the library '''
        STR_ADDING_ALL_x_SEASONS_WITH_METADATA = 'Adding all %s seasons with metadata...'
        STR_ALL_x_SEASONS_WITH_METADATA_ADDED = 'All %s seasons with metadata added'
        staged_seasons = self.dbh.get_content_items(
            status='staged', mediatype='tvshow', order='Show_Title', show_title=show_title
        )

        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create(
            ADDON_NAME, STR_ADDING_ALL_x_SEASONS_WITH_METADATA % show_title
        )
        for index, item in enumerate(staged_seasons):
            percent = 100 * index / len(staged_seasons)

            if os.path.exists(item.episode_nfo[0]):
                progress_dialog.update(
                    int(percent),
                    '\n'.join([item.show_title, item.episode_title_with_id])
                )
                xbmc.sleep(200)
                item.add_to_library()

            progress_dialog.update(int(percent), '\n'.join([' ', ' ']))
        progress_dialog.close()
        notification(STR_ALL_x_SEASONS_WITH_METADATA_ADDED % show_title)


    @staticmethod
    @logged_function
    # TODO: revise this function >> add_all_episodes_with_metadata
    def add_all_episodes_with_metadata(staged_episodes, show_title):
        ''' Add all episodes in the specified show with metadata to the library '''
        STR_ADDING_ALL_x_EPISODES_WITH_METADATA = getlocalizedstring(32073)
        STR_ALL_x_EPISODES_WITH_METADATA_ADDED = getlocalizedstring(32074)
        show_title = items[0]
        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create(
            ADDON_NAME, STR_ADDING_ALL_x_EPISODES_WITH_METADATA % show_title
        )
        for index, item in enumerate(items):
            percent = 100 * index / len(items)
            # nfo_path = os.path.join(metadata_dir, item.clean_title + '.nfo')
            if os.path.exists(item.episode_nfo[0]):
                progress_dialog.update(
                    int(percent),
                    item.show_title,
                    item.episode_title_with_id
                )
                xbmc.sleep(200)
                item.add_to_library()
            progress_dialog.update(int(percent), '\n'.join([' ', ' ']))
        progress_dialog.close()
        notification(STR_ALL_x_EPISODES_WITH_METADATA_ADDED % show_title)


    @staticmethod
    @logged_function
    def generate_all_episodes_metadata(items):
        ''' Generate metadata items for all episodes in show '''
        STR_GENERATING_ALL_x_METADATA = getlocalizedstring(32077)
        STR_ALL_x_METADATA_CREATED = getlocalizedstring(32078)
        show_title = items[0].show_title
        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create(ADDON_NAME, STR_GENERATING_ALL_x_METADATA % show_title)
        for index, item in enumerate(items):
            percent = 100 * index / len(items)
            progress_dialog.update(int(percent), '\n'.join([item.show_title, item.episode_title_with_id]))
            xbmc.sleep(200)
            item.create_metadata_item()
        progress_dialog.close()
        notification(STR_ALL_x_METADATA_CREATED % show_title)


    @logged_function
    def generate_all_seasons_metadata(self, show_title):
        ''' Generate metadata items for all seasons in show '''
        STR_GENERATING_ALL_x_METADATA = 'Generating all %s metadata...'
        STR_ALL_x_METADATA_CREATED = 'All %s metadata created'

        staged_seasons = self.dbh.get_content_items(
            status='staged', mediatype='tvshow', order='Show_Title', show_title=show_title
        )

        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create(ADDON_NAME, STR_GENERATING_ALL_x_METADATA % show_title)

        for index, item in enumerate(staged_seasons):
            percent = 100 * index / len(staged_seasons)
            progress_dialog.update(int(percent), '\n'.join([item.show_title, item.episode_title_with_id]))
            xbmc.sleep(200)
            item.create_metadata_item()

        progress_dialog.close()
        notification(STR_ALL_x_METADATA_CREATED % show_title)


    @staticmethod
    def rename_dialog(item):
        ''' Prompt input for new name, and rename if non-empty string '''
        input_ret = xbmcgui.Dialog().input("Title", defaultt=item.show_title)
        if input_ret:
            item.rename(input_ret)


    @staticmethod
    @logged_function
    def rename_episodes_using_metadata(items):
        ''' Rename all episodes in show using nfo files '''
        STR_RENAMING_x_EPISODES_USING_METADATA = getlocalizedstring(32075)
        STR_x_EPISODES_RENAMED_USING_METADATA = getlocalizedstring(32076)
        show_title = items[0].show_title
        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create(
            ADDON_NAME, STR_RENAMING_x_EPISODES_USING_METADATA % show_title
        )
        for index, item in enumerate(items):
            percent = 100 * index / len(items)
            progress_dialog.update(int(percent), '\n'.join([item.show_title, item.episode_title_with_id]))
            xbmc.sleep(200)
            # TODO: fix rename_using_metadata() current is not used
            # item.rename_using_metadata()
        progress_dialog.close()
        notification(STR_x_EPISODES_RENAMED_USING_METADATA % show_title)


    @logged_function
    def add_all_shows(self):
        ''' Add all tvshow items to library '''
        STR_ADDING_ALL_TV_SHOWS = getlocalizedstring(32059)
        STR_ALL_TV_SHOWS_ADDED = getlocalizedstring(32060)
        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create(ADDON_NAME, STR_ADDING_ALL_TV_SHOWS)
        staged_tv_items = self.dbh.get_content_items(
            status='staged', mediatype='tvshow', order='Show_Title'
        )
        for index, item in enumerate(staged_tv_items):
            percent = 100 * index / len(staged_tv_items)
            progress_dialog.update(int(percent), '\n'.join([item.show_title, item.episode_title_with_id]))
            xbmc.sleep(200)
            item.add_to_library()
        progress_dialog.close()
        notification(STR_ALL_TV_SHOWS_ADDED)


    @logged_function
    def add_all_with_metadata(self):
        ''' Add all tvshow items with nfo file to library'''
        STR_ADDING_ALL_TV_SHOW_ITEMS_WITH_METADATA = getlocalizedstring(32061)
        STR_ALL_TV_SHOW_ITEMS_WITH_METADATA_ADDED = getlocalizedstring(32062)
        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create(ADDON_NAME, STR_ADDING_ALL_TV_SHOW_ITEMS_WITH_METADATA)

        staged_tv_items = self.dbh.get_content_items(
            status='staged', mediatype='tvshow', order='Show_Title'
        )
        # content menaget precisa retornar episode_nfo[0]
        for index, item in enumerate(staged_tv_items):
            percent = 100 * index / len(staged_tv_items)
            if os.path.exists(item.episode_nfo[0]):
                progress_dialog.update(
                    int(percent),
                    '\n'.join([item.show_title, item.episode_title_with_id])
                )
                xbmc.sleep(200)
                item.add_to_library()
            progress_dialog.update(int(percent), '\n'.join([' ', ' ']))
        progress_dialog.close()
        notification(STR_ALL_TV_SHOW_ITEMS_WITH_METADATA_ADDED)


    @logged_function
    def generate_all_metadata(self):
        ''' Create metadata for all staged tvshow items '''
        STR_GENERATING_ALL_TV_SHOW_METADATA = getlocalizedstring(32063)
        STR_ALL_TV_SHOW_METADATA_CREATED = getlocalizedstring(32064)
        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create(ADDON_NAME, STR_GENERATING_ALL_TV_SHOW_METADATA)
        staged_tv_items = self.dbh.get_content_items(
            status='staged', mediatype='tvshow', order='Show_Title'
        )
        for index, item in enumerate(staged_tv_items):
            percent = 100 * index / len(staged_tv_items)
            progress_dialog.update(int(percent), '\n'.join([item.show_title]))
            xbmc.sleep(200)
            item.create_metadata_item()
        progress_dialog.close()
        notification(STR_ALL_TV_SHOW_METADATA_CREATED)


    @logged_function
    def read_all_metadata(self):
        ''' Read metadata for all staged tvshow items '''
        STR_READING_ALL_TV_SHOW_METADATA = getlocalizedstring(32145)
        STR_ALL_TV_SHOW_METADATA_READ = getlocalizedstring(32146)
        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create(ADDON_NAME, STR_READING_ALL_TV_SHOW_METADATA)
        staged_tv_items = self.dbh.get_content_items(
            status='staged', mediatype='tvshow', order='Show_Title'
        )
        for index, item in enumerate(staged_tv_items):
            percent = 100 * index / len(staged_tv_items)
            progress_dialog.update(int(percent), '\n'.join([item.show_title]))
            xbmc.sleep(200)
            # item.read_metadata_item()
        progress_dialog.close()
        notification(STR_ALL_TV_SHOW_METADATA_READ)

    @logged_function
    def remove_all(self):
        ''' Remove all staged tvshow items '''
        STR_REMOVING_ALL_TV_SHOWS = getlocalizedstring(32024)
        STR_ALL_TV_SHOW_REMOVED = getlocalizedstring(32025)
        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create(ADDON_NAME, STR_REMOVING_ALL_TV_SHOWS)
        self.dbh.remove_from(
            status='staged',
            mediatype='tvshow',
            show_title=None,
            directory=None
        )
        progress_dialog.close()
        notification(STR_ALL_TV_SHOW_REMOVED)


    @logged_function
    def remove_all_seasons(self, show_title):
        ''' Remove all seasons from the specified show '''
        STR_REMOVING_ALL_x_SEASONS = getlocalizedstring(32032) % show_title
        STR_ALL_x_SEASONS_REMOVED = getlocalizedstring(32033) % show_title
        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create(ADDON_NAME, STR_REMOVING_ALL_x_SEASONS)
        self.dbh.remove_from(
            status='staged',
            mediatype='tvshow',
            show_title=show_title,
            directory=None
        )
        progress_dialog.close()
        notification(STR_ALL_x_SEASONS_REMOVED)


    @logged_function
    def remove_all_episodes(self, show_title):
        ''' Remove all episodes from the specified show '''
        STR_REMOVING_ALL_x_EPISODES = getlocalizedstring(32032) % show_title
        STR_ALL_x_EPISODES_REMOVED = getlocalizedstring(32033) % show_title
        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create(ADDON_NAME, STR_REMOVING_ALL_x_EPISODES)
        self.dbh.remove_from(
            status='staged',
            mediatype='tvshow',
            show_title=show_title,
            directory=None
        )
        progress_dialog.close()
        notification(STR_ALL_x_EPISODES_REMOVED)


    @logged_function
    def remove_and_block_show(self, show_title):
        ''' Remove all seasons from specified show from the library,
        delete metadata, and add to blocked list '''
        # Remove from staged
        self.remove_all_seasons(show_title)
        # Delete metadata folder
        clean_show_title = clean_name(show_title)
        metadata_dir = os.path.join(METADATA_FOLDER, 'TV', clean_show_title)
        remove_dir(metadata_dir)
        # Add show title to blocked
        self.dbh.add_blocked_item(show_title, 'tvshow')


    @logged_function
    def episode_options(self, item, season_number):
        ''' Provide options for a single staged episode in a dialog window '''
        #TODO: rename associated metadata when renaming
        #TODO: rename show title
        #TODO: remove item (including metadata)
        STR_ADD = getlocalizedstring(32048)
        STR_REMOVE = getlocalizedstring(32017)
        STR_REMOVE_AND_BLOCK_EPISODE = getlocalizedstring(32079)
        STR_RENAME = getlocalizedstring(32050)
        STR_AUTOMATICALLY_RENAME_USING_METADTA = getlocalizedstring(
            32051)
        STR_GENERATE_METADATA_ITEM = getlocalizedstring(32052)
        STR_BACK = getlocalizedstring(32011)
        STR_STAGED_EPISODE_OPTIONS = getlocalizedstring(32080)
        lines = [
            STR_ADD, STR_REMOVE, STR_REMOVE_AND_BLOCK_EPISODE, STR_RENAME,
            STR_AUTOMATICALLY_RENAME_USING_METADTA, STR_GENERATE_METADATA_ITEM, STR_BACK
        ]
        ret = xbmcgui.Dialog().select(
            '{0} - {1} - {2}'.format(ADDON_NAME,
                                     STR_STAGED_EPISODE_OPTIONS, item.show_title),
            lines
        )
        if ret >= 0:
            if lines[ret] == STR_ADD:
                item.add_to_library()
                self.view_episodes(item.show_title, season_number)
            elif lines[ret] == STR_REMOVE:
                item.delete()
                self.view_episodes(item.show_title, season_number)
            elif lines[ret] == STR_REMOVE_AND_BLOCK_EPISODE:
                item.remove_and_block()
                self.view_episodes(item.show_title, season_number)
            elif lines[ret] == STR_RENAME:
                self.rename_dialog(item)
                self.episode_options(item, season_number)
            elif lines[ret] == STR_GENERATE_METADATA_ITEM:
                item.create_metadata_item()
                self.episode_options(item, season_number)
            elif lines[ret] == STR_AUTOMATICALLY_RENAME_USING_METADTA:
                item.rename_using_metadata()
                self.episode_options(item, season_number)
            elif lines[ret] == STR_BACK:
                self.view_episodes(item.show_title, season_number)
        else:
            self.view_episodes(item.show_title, season_number)


    @logged_function
    def view_episodes(self, show_title, season_number):
        ''' Display all staged episodes in the specified show,
        which are selectable and lead to options.
        Also provides additional options at bottom of menu '''
        STR_NO_STAGED_x_EPISODES = getlocalizedstring(32065) % show_title
        STR_ADD_ALL_EPISODES = getlocalizedstring(32066)
        STR_ADD_ALL_EPISODES_WITH_METADATA = getlocalizedstring(32067)
        STR_REMOVE_ALL_EPISODES = getlocalizedstring(32029)
        STR_REMOVE_AND_BLOCK_TV_SHOW = getlocalizedstring(32068)
        STR_AUTOMATICALLY_RENAME_ALL_EPISODES_USING_METADATA = getlocalizedstring(32069)
        STR_GENERATE_ALL_METADATA_ITEMS = getlocalizedstring(32040)
        STR_BACK = getlocalizedstring(32011)
        STR_STAGED_x_EPISODES = getlocalizedstring(32070) % show_title
        staged_episodes = self.dbh.get_content_items(
            status='staged',
            mediatype='tvshow',
            order='Show_Title',
            show_title=show_title,
            season_number=season_number
        )
        if not staged_episodes:
            xbmcgui.Dialog().ok(
                ADDON_NAME,
                STR_NO_STAGED_x_EPISODES
            )
            self.view_shows()
            return
        lines = [str(x) for x in staged_episodes]
        lines += [
            STR_ADD_ALL_EPISODES, STR_ADD_ALL_EPISODES_WITH_METADATA, STR_REMOVE_ALL_EPISODES,
            STR_REMOVE_AND_BLOCK_TV_SHOW, STR_AUTOMATICALLY_RENAME_ALL_EPISODES_USING_METADATA,
            STR_GENERATE_ALL_METADATA_ITEMS, STR_BACK
        ]
        ret = xbmcgui.Dialog().select(
            '{0} - {1}'.format(ADDON_NAME, STR_STAGED_x_EPISODES), lines
        )
        if ret >= 0:
            if ret < len(staged_episodes):  # staged item
                for i, item in enumerate(staged_episodes):
                    if ret == i:
                        self.episode_options(item, season_number)
                        break
            elif lines[ret] == STR_ADD_ALL_EPISODES:
                self.add_all_episodes(staged_episodes)
                self.view_shows()
            elif lines[ret] == STR_ADD_ALL_EPISODES_WITH_METADATA:
                self.add_all_episodes_with_metadata(staged_episodes, show_title)
                self.view_episodes(show_title, season_number)
            elif lines[ret] == STR_REMOVE_ALL_EPISODES:
                self.remove_all_episodes(show_title)
                self.view_shows()
            elif lines[ret] == STR_REMOVE_AND_BLOCK_TV_SHOW:
                self.remove_and_block_show(show_title)
                self.view_shows()
            elif lines[ret] == STR_AUTOMATICALLY_RENAME_ALL_EPISODES_USING_METADATA:
                self.rename_episodes_using_metadata(staged_episodes)
                self.view_episodes(show_title, season_number)
            elif lines[ret] == STR_GENERATE_ALL_METADATA_ITEMS:
                self.generate_all_episodes_metadata(staged_episodes)
                self.view_episodes(show_title, season_number)
            elif lines[ret] == STR_BACK:
                self.view_seasons(show_title)
        else:
            self.view_seasons(show_title)


    @logged_function
    def view_seasons(self, show_title):
        ''' Display all staged seasons in the specified show,
        which are selectable and lead to options.
        Also provides additional options at bottom of menu '''
        STR_NO_STAGED_x_SEASONS = 'No staged %s seasons' % show_title
        STR_ADD_ALL_SEASONS = 'Add all seasons'
        STR_ADD_ALL_SEASONS_WITH_METADATA = 'Add all seasons with metadata'
        STR_REMOVE_ALL_SEASONS = 'Remove all seasons'
        STR_REMOVE_AND_BLOCK_TV_SHOW = getlocalizedstring(32068)
        STR_AUTOMATICALLY_RENAME_ALL_SEASONS_USING_METADATA = getlocalizedstring(32069)
        STR_GENERATE_ALL_METADATA_ITEMS = getlocalizedstring(32040)
        STR_BACK = getlocalizedstring(32011)
        STR_STAGED_x_SEASONS = 'Staged %s seasons' % show_title
        staged_seasons = self.dbh.get_content_items(
            status='staged', mediatype='tvshow', order='Season', show_title=show_title
        )
        if not staged_seasons:
            xbmcgui.Dialog().ok(ADDON_NAME, STR_NO_STAGED_x_SEASONS)
            self.view_shows()
            return

        lines = [str('[B]Season %s[/B]' % x) for x in staged_seasons]
        lines += [
            STR_ADD_ALL_SEASONS, STR_ADD_ALL_SEASONS_WITH_METADATA, STR_REMOVE_ALL_SEASONS,
            STR_REMOVE_AND_BLOCK_TV_SHOW, STR_AUTOMATICALLY_RENAME_ALL_SEASONS_USING_METADATA,
            STR_GENERATE_ALL_METADATA_ITEMS, STR_BACK
        ]
        ret = xbmcgui.Dialog().select(
            '{0} - {1}'.format(ADDON_NAME, STR_STAGED_x_SEASONS), lines
        )
        selection = lines[ret]
        if ret >= 0:
            if selection == STR_ADD_ALL_SEASONS:
                self.add_all_seasons(show_title)
                self.view_shows()
            elif selection == STR_ADD_ALL_SEASONS_WITH_METADATA:
                self.add_all_seasons_with_metadata(show_title)
                self.view_seasons(show_title)
            elif selection == STR_REMOVE_ALL_SEASONS:
                self.remove_all_seasons(show_title)
                self.view_shows()
            elif selection == STR_REMOVE_AND_BLOCK_TV_SHOW:
                self.remove_and_block_show(show_title)
                self.view_shows()
            elif (selection ==
                  STR_AUTOMATICALLY_RENAME_ALL_SEASONS_USING_METADATA):
                self.rename_seasons_using_metadata(staged_seasons)
                self.view_seasons(show_title)
            elif selection == STR_GENERATE_ALL_METADATA_ITEMS:
                self.generate_all_seasons_metadata(show_title)
                self.view_seasons(show_title)
            elif selection == STR_BACK:
                self.view_shows()
            else:  # staged item
                self.view_episodes(
                    show_title,
                    season_number=''.join(filter(str.isdigit, selection))
                )
        else:
            self.view_shows()


    @logged_function
    def view_shows(self):
        ''' Display all managed tvshows, which are selectable and lead to options.
        Also provides additional options at bottom of menu '''
        STR_NO_STAGED_TV_SHOWS = getlocalizedstring(32054)
        STR_ADD_ALL_TV_SHOWS = getlocalizedstring(32055)
        STR_ADD_ALL_ITEMS_WITH_METADTA = getlocalizedstring(32056)
        STR_REMOVE_ALL_TV_SHOWS = getlocalizedstring(32057)
        STR_GENERATE_ALL_METADATA_ITEMS = getlocalizedstring(32040)
        STR_READ_ALL_METADATA_ITEMS = getlocalizedstring(32147)
        STR_BACK = getlocalizedstring(32011)
        STR_STAGED_TV_SHOWS = getlocalizedstring(32058)
        staged_tvshows = self.dbh.get_all_shows('staged')
        if not staged_tvshows:
            xbmcgui.Dialog().ok(ADDON_NAME, STR_NO_STAGED_TV_SHOWS)
            return
        lines = ['[B]{}[/B]'.format(x) for x in staged_tvshows]
        lines += [
            STR_ADD_ALL_TV_SHOWS, STR_ADD_ALL_ITEMS_WITH_METADTA, STR_REMOVE_ALL_TV_SHOWS,
            STR_GENERATE_ALL_METADATA_ITEMS, STR_READ_ALL_METADATA_ITEMS, STR_BACK
        ]
        ret = xbmcgui.Dialog().select(
            '{0} - {1}'.format(ADDON_NAME, STR_STAGED_TV_SHOWS), lines
        )
        if ret >= 0:
            if ret < len(staged_tvshows):  # staged item
                for show_title in staged_tvshows:
                    if staged_tvshows[ret] == show_title:
                        self.view_seasons(show_title)
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
