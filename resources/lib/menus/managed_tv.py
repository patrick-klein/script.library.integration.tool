#!/usr/bin/python
# -*- coding: utf-8 -*-

'''Defines the ManagedTVMenu class'''

import xbmc # pylint: disable=import-error
import xbmcgui # pylint: disable=import-error


from resources import ADDON_NAME
from resources.lib.log import logged_function

from resources.lib.utils import notification
from resources.lib.utils import getlocalizedstring


class ManagedTVMenu(object):
    '''Provide windows for displaying managed shows and episodes,
    and tools for manipulating the objects and managed file'''

    def __init__(self):
        self.dbh = Database()


    @staticmethod
    @logged_function
        '''Remove all managed episodes in specified show from library, and add them to staged'''
        STR_MOVING_ALL_x_EPISODES_BACK_TO_STAGED = getlocalizedstring(32034)
        STR_ALL_x_EPISODES_MOVED_TO_STAGED = getlocalizedstring(32035)
        show_title = items[0].show_title
        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create(
            ADDON_NAME, STR_MOVING_ALL_x_EPISODES_BACK_TO_STAGED % show_title
        )
        for index, item in enumerate(items):
            percent = 100 * index / len(items)
            progress_dialog.update(
                int(percent), message='\n'.join([item.show_title, item.episode_title_with_id])
            )
            xbmc.sleep(200)
            item.remove_from_library()
            item.set_as_staged()
        progress_dialog.close()
        notification(STR_ALL_x_EPISODES_MOVED_TO_STAGED % show_title)


    @logged_function
    def move_all_seasons_to_staged(self, show_title):
        '''Remove all managed episodes in specified show from library, and add them to staged'''
        STR_MOVING_ALL_x_SEASONS_BACK_TO_STAGED = 'Movendo temporadas de %s para staged'
        STR_ALL_x_SEASONS_MOVED_TO_STAGED = 'Todas as temporadas de %s movidas para staged'
        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create(
            ADDON_NAME, STR_MOVING_ALL_x_SEASONS_BACK_TO_STAGED % show_title
        )
        items = self.dbh.get_content_items(
            status='managed', mediatype='tvshow', show_title=show_title, order='Show_Title'
        )
        for index, item in enumerate(items):
            percent = 100 * index / len(items)
            progress_dialog.update(
                int(percent), message='\n'.join([item.show_title, item.episode_title_with_id])
            )
            xbmc.sleep(200)
            item.remove_from_library()
            item.set_as_staged()
        progress_dialog.close()
        notification(STR_ALL_x_SEASONS_MOVED_TO_STAGED % show_title)


    @logged_function
    def move_all_to_staged(self):
        '''Remove all managed tvshow items from library, and add them to staged'''
        STR_MOVING_ALL_TV_SHOWS_BACK_TO_STAGED = getlocalizedstring(32026)
        STR_ALL_TV_SHOWS_MOVED_TO_STAGED = getlocalizedstring(32027)
        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create(ADDON_NAME, STR_MOVING_ALL_TV_SHOWS_BACK_TO_STAGED)

        managed_tv_items = self.dbh.get_content_items(
            status='managed', mediatype='tvshow', order='Show_Title'
        )
        for index, item in enumerate(managed_tv_items):
            percent = 100 * index / len(managed_tv_items)
            progress_dialog.update(int(percent), message='\n'.join([item.show_title, item.episode_title_with_id]))

            xbmc.sleep(200)
            item.remove_from_library()
            item.set_as_staged()
        progress_dialog.close()
        notification(STR_ALL_TV_SHOWS_MOVED_TO_STAGED)


    @staticmethod
    @logged_function
        '''Remove all episodes in specified show from library'''
        STR_REMOVING_ALL_x_EPISODES = getlocalizedstring(32032)
        STR_ALL_x_EPISODES_REMOVED = getlocalizedstring(32033)
        show_title = items[0].show_title
        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create(ADDON_NAME, STR_REMOVING_ALL_x_EPISODES % show_title)
        for index, item in enumerate(items):
            percent = 100 * index / len(items)
            progress_dialog.update(
                int(percent), message='\n'.join([item.show_title, item.episode_title_with_id])
            )
            item.remove_from_library()
            item.delete()
        progress_dialog.close()
        notification(STR_ALL_x_EPISODES_REMOVED % show_title)


    @logged_function
    def remove_seasons(self, items, show_title):
        '''Remove all seasons in specified show from library'''
        STR_REMOVING_ALL_X_SEASONS = 'Removendo temporadas de: %s'
        STR_ALL_X_SEASONS_REMOVED = 'Todas as temporadas de %s, foram removidas'
        seasons = items[0]
        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create(ADDON_NAME, STR_REMOVING_ALL_X_SEASONS % show_title)

        for season_number in seasons:
            percent = 100 * season_number / len(seasons)
            progress_dialog.update(
                int(percent),
                message='\n'.join([show_title,
                str("Season: %s" % season_number)])
            )
            self.dbh.remove_from(mediatype='tvshow', show_title=show_title, season=season_number)
            xbmc.sleep(300)
        progress_dialog.close()
        notification(STR_ALL_X_SEASONS_REMOVED % show_title)


    @logged_function
    def remove_all(self):
        '''Remove all managed tvshow items from library'''
        STR_REMOVING_ALL_TV_SHOWS = getlocalizedstring(32024)
        STR_ALL_TV_SHOWS_REMOVED = getlocalizedstring(32025)
        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create(ADDON_NAME, STR_REMOVING_ALL_TV_SHOWS)
        managed_tv_items = self.dbh.get_content_items(
            status='managed', mediatype='tvshow', order='Show_Title'
        )
        for index, item in enumerate(managed_tv_items):
            percent = 100 * index / len(managed_tv_items)
            progress_dialog.update(int(percent), message='\n'.join([item.show_title, item.episode_title_with_id]))

            item.remove_from_library()
            item.delete()
        progress_dialog.close()
        notification(STR_ALL_TV_SHOWS_REMOVED)


    @logged_function
    def episode_options(self, item, season_number):
        '''Provide options for a single managed episode in a dialog window'''
        STR_REMOVE = getlocalizedstring(32017)
        STR_MOVE_BACK_TO_STAGED = getlocalizedstring(32018)
        STR_BACK = getlocalizedstring(32011)
        STR_MANAGED_EPISODE_OPTIONS = getlocalizedstring(32036)
        lines = [STR_REMOVE, STR_MOVE_BACK_TO_STAGED, STR_BACK]
        ret = xbmcgui.Dialog().select(
            '{0} - {1} - {2}'.format(
                ADDON_NAME, STR_MANAGED_EPISODE_OPTIONS, item.episode_title_with_id
            ),
            lines
        )
        if ret >= 0:
            if lines[ret] == STR_REMOVE:
                item.remove_from_library()
                item.delete()
                return self.view_episodes(item.show_title, season_number)
            elif lines[ret] == STR_MOVE_BACK_TO_STAGED:
                item.remove_from_library()
                item.set_as_staged()
                return self.view_episodes(item.show_title, season_number)
            elif lines[ret] == STR_BACK:
                return self.view_episodes(item.show_title, season_number)
        return self.view_episodes(item.show_title, season_number)


    @logged_function
    def view_episodes(self, show_title, season_number):
        '''Displays all managed episodes in the specified show,
        which are selectable and lead to options.
        Also provides additional options at bottom of menu'''
        STR_NO_MANAGED_x_EPISODES = getlocalizedstring(32028) % show_title
        STR_REMOVE_ALL_EPISODES = getlocalizedstring(32029)
        STR_MOVE_ALL_EPISODES_BACK_TO_STAGED = getlocalizedstring(32030)
        STR_BACK = getlocalizedstring(32011)
        STR_MANAGED_x_EPISODES = getlocalizedstring(32031) % show_title
        managed_episodes = self.dbh.get_content_items(
            status='managed',
            mediatype='tvshow',
            order='Show_Title',
            show_title=show_title,
            season_number=season_number
        )
        if not managed_episodes:
            xbmcgui.Dialog().ok(ADDON_NAME, STR_NO_MANAGED_x_EPISODES)
            return self.view_shows()
        lines = [str(x) for x in managed_episodes]
        lines += [STR_REMOVE_ALL_EPISODES, STR_MOVE_ALL_EPISODES_BACK_TO_STAGED, STR_BACK]
        ret = xbmcgui.Dialog().select(
            '{0} - {1}'.format(ADDON_NAME, STR_MANAGED_x_EPISODES), lines
        )
        if ret >= 0:
            if ret < len(managed_episodes):  # managed item
                for i, item in enumerate(managed_episodes):
                    if ret == i:
                        return self.episode_options(item, season_number)
            elif lines[ret] == STR_REMOVE_ALL_EPISODES:
                self.remove_episodes(managed_episodes)
                return self.view_shows()
            elif lines[ret] == STR_MOVE_ALL_EPISODES_BACK_TO_STAGED:
                self.move_episodes_to_staged(managed_episodes)
                return self.view_shows()
            elif lines[ret] == STR_BACK:
                return self.view_seasons(show_title)
        return self.view_seasons(show_title)


    @logged_function
    def view_seasons(self, show_title):
        '''Displays all managed seasons in the specified show,
        which are selectable and lead to options.
        Also provides additional options at bottom of menu'''
        # TODO: functions to remove all or add all if necessary
        STR_NO_MANAGED_X_SEASONS = str('No managed %s seasons') % show_title
        STR_REMOVE_ALL_SEASONS = 'Remove all seasons'
        STR_MOVE_ALL_SEASONS_BACK_TO_STAGED = 'Move all seasons back to staged'
        STR_BACK = getlocalizedstring(32011)
        STR_MANAGED_X_SEASONS = str('Managed %s Seasons') % show_title
        managed_seasons = self.dbh.get_content_items(
            status='managed', mediatype='tvshow', order='Season', show_title=show_title
        )
        if not managed_seasons:
            xbmcgui.Dialog().ok(ADDON_NAME, STR_NO_MANAGED_X_SEASONS)
            return self.view_shows()
        lines = [str('[B]Season %s[/B]' % x) for x in managed_seasons]
        lines += [
            STR_REMOVE_ALL_SEASONS, STR_MOVE_ALL_SEASONS_BACK_TO_STAGED, STR_BACK
        ]
        ret = xbmcgui.Dialog().select(
            '{0} - {1}'.format(ADDON_NAME, STR_MANAGED_X_SEASONS), lines
        )
        selection = lines[ret]
        if ret >= 0:
            if selection == STR_REMOVE_ALL_SEASONS:
                # TODO: remove by title only
                self.remove_seasons(managed_seasons, show_title)
                return self.view_shows()
            elif selection == STR_MOVE_ALL_SEASONS_BACK_TO_STAGED:
                self.move_all_seasons_to_staged(show_title)
                return self.view_shows()
            elif selection == STR_BACK:
                self.view_shows()
                return self.view_shows()
            else:  # managed item
                return self.view_episodes(
                    show_title=show_title,
                    season_number=''.join(filter(str.isdigit, selection)))
        return self.view_shows()


    @logged_function
    def view_shows(self):
        '''Display all managed tvshows, which are selectable and lead to options.
        Also provides additional options at bottom of menu'''
        STR_NO_MANAGED_TV_SHOWS = getlocalizedstring(32020)
        STR_REMOVE_ALL_TV_SHOWS = getlocalizedstring(32021)
        STR_MOVE_ALL_TV_SHOWS_BACK_TO_STAGED = getlocalizedstring(32022)
        STR_BACK = getlocalizedstring(32011)
        STR_MANAGED_TV_SHOWS = getlocalizedstring(32023)
        managed_tvshows = self.dbh.get_all_shows('managed')
        if not managed_tvshows:
            xbmcgui.Dialog().ok(ADDON_NAME, STR_NO_MANAGED_TV_SHOWS)
            return
        lines = ['[B]{}[/B]'.format(x) for x in managed_tvshows]
        lines += [
            STR_REMOVE_ALL_TV_SHOWS, STR_MOVE_ALL_TV_SHOWS_BACK_TO_STAGED, STR_BACK
        ]
        ret = xbmcgui.Dialog().select(
            '{0} - {1}'.format(ADDON_NAME, STR_MANAGED_TV_SHOWS), lines
        )
        if ret >= 0:
            if ret < len(managed_tvshows):
                for show_title in managed_tvshows:
                    if managed_tvshows[ret] == show_title:
                        self.view_seasons(show_title)
                        break
            elif lines[ret] == STR_REMOVE_ALL_TV_SHOWS:
                self.remove_all()
            elif lines[ret] == STR_MOVE_ALL_TV_SHOWS_BACK_TO_STAGED:
                self.move_all_to_staged()
            elif lines[ret] == STR_BACK:
                return
