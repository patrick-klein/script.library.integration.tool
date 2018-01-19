#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import cPickle as pickle
import simplejson as json
import xbmc
import xbmcgui
import xbmcaddon

from contentitem import MovieItem, EpisodeItem
from utils import log_msg, get_items, save_items, append_item, remove_item, clean, localize_mediatype

managed_folder = '/Volumes/Drobo Media/LibraryTools/'

class Main(object):
    #TODO: use staticmethod tag and maybe move some methods to utils
    #TODO: define strings here (and eventually localize)
    #TODO: use sqlite database... will lead to LOTS of optimizations
    #TODO: unit tests
    #TODO: pass around a 'previous view' function handle
    #TODO: mark strm items as watched after played

    addon = xbmcaddon.Addon()
    str_addon_name  = addon.getAddonInfo('name')

    def __init__(self):
        self.choose_action()

    def choose_action(self):
        #TODO: fix update library to only update path
        #TODO: view by show title
        #TODO: remove extraneous tv show folders in Metadata
        #TODO: add all items with metadata
        #?TODO: add all from here
        #?TODO: view all
        #TODO: rebuild managed list (remove all items, then re-add new instance of ContentItem)
        #TODO: add parameter for location in list - useful when returning here after doing something on an item (preselct is broken when pressing cancel)
        str_view_managed_movies = self.addon.getLocalizedString(32002)
        str_view_managed_tv_shows = self.addon.getLocalizedString(32003)
        str_view_staged_movies = self.addon.getLocalizedString(32004)
        str_view_staged_tv_shows = self.addon.getLocalizedString(32005)
        str_view_synced_directories = self.addon.getLocalizedString(32006)
        str_view_blocked_items = self.addon.getLocalizedString(32007)
        str_update_library = xbmc.getLocalizedString(653)
        str_clean_library = xbmc.getLocalizedString(14247)

        lines = [str_view_managed_movies, str_view_managed_tv_shows, str_view_staged_movies, str_view_staged_tv_shows,
            str_view_synced_directories, str_view_blocked_items, str_update_library, str_clean_library]
        ret = xbmcgui.Dialog().select(self.str_addon_name, lines)
        if not ret<0:
            if lines[ret] == str_view_managed_movies:
                self.view_managed_movies()
            elif lines[ret] == str_view_managed_tv_shows:
                self.view_managed_tvshows()
            elif lines[ret] == str_view_staged_movies:
                self.view_staged_movies()
            elif lines[ret] == str_view_staged_tv_shows:
                self.view_staged_tvshows()
            elif lines[ret] == str_view_synced_directories:
                self.view_synced()
            elif lines[ret] == str_view_blocked_items:
                self.view_blocked()
            elif lines[ret] == str_update_library:
                xbmc.executebuiltin('UpdateLibrary("video")')
            elif lines[ret] == str_clean_library:
                xbmc.executebuiltin('CleanLibrary("video")')

    def view_managed_movies(self):
        str_no_managed_movies = self.addon.getLocalizedString(32008)
        str_remove_all_movies = self.addon.getLocalizedString(32009)
        str_move_all_movies_back_to_staged = self.addon.getLocalizedString(32010)
        str_back = self.addon.getLocalizedString(32011)
        str_managed_movies = self.addon.getLocalizedString(32012)

        managed_items = get_items('managed.pkl')
        managed_movies = [x for x in managed_items if x.get_mediatype()=='movie']
        if len(managed_movies)==0:
            xbmcgui.Dialog().ok(self.str_addon_name, str_no_managed_movies)
            return self.choose_action()
        lines = [str(x) for x in managed_movies]
        lines, managed_movies = (list(t) for t in zip(*sorted(zip(lines, managed_movies), key=lambda x: x[0].lower())))
        lines += [str_remove_all_movies, str_move_all_movies_back_to_staged, str_back]
        ret = xbmcgui.Dialog().select('{0} - {1}'.format(self.str_addon_name, str_managed_movies), lines)
        if not ret<0:
            if ret<len(managed_movies):   # managed item
                for i, item in enumerate(managed_movies):
                    if ret==i:
                        self.managed_movie_options(item)
            elif lines[ret] == str_remove_all_movies:
                self.remove_all_managed_movies()
                return self.choose_action()
            elif lines[ret] == str_move_all_movies_back_to_staged:
                self.move_all_managed_movies_to_staged()
                return self.choose_action()
            elif lines[ret] == str_back:
                return self.choose_action()
        else:
            self.choose_action()

    def remove_all_managed_movies(self):
        str_removing_all_movies = self.addon.getLocalizedString(32013)
        str_all_movies_removed = self.addon.getLocalizedString(32014)

        pDialog = xbmcgui.DialogProgress()
        pDialog.create(self.str_addon_name, str_removing_all_movies)
        managed_items = get_items('managed.pkl')
        for item in managed_items:
            if item.get_mediatype()=='movie':
                pDialog.update(0,line2=item.get_title())
                item.remove_from_library()
            else:
                pDialog.update(0,line2=' ')
        pDialog.close()
        xbmc.executebuiltin('Notification("{0}", "{1}")'.format(self.str_addon_name, str_all_movies_removed))

    def move_all_managed_movies_to_staged(self):
        str_moving_all_movies_back_to_staged = self.addon.getLocalizedString(32015)
        str_all_movies_movied_to_staged = self.addon.getLocalizedString(32016)

        pDialog = xbmcgui.DialogProgress()
        pDialog.create(self.str_addon_name, str_moving_all_movies_back_to_staged)
        managed_items = get_items('managed.pkl')
        for item in managed_items:
            if item.get_mediatype()=='movie':
                pDialog.update(0,line2=item.get_title())
                item.add_to_staged_file()
                item.remove_from_library()
            else:
                pDialog.update(0,line2=' ')
        pDialog.close()
        xbmc.executebuiltin('Notification("{0}", "{1}")'.format(self.str_addon_name, str_all_movies_movied_to_staged))

    def managed_movie_options(self, item):
        # TODO: add rename option
        # TODO: add reload metadata option
        # TODO: move back to staging
        # TODO: change item.show_title to item.get_show_title after I've rebuilt library
        str_remove = self.addon.getLocalizedString(32017)
        str_move_back_to_staged = self.addon.getLocalizedString(32018)
        str_back = self.addon.getLocalizedString(32011)
        str_managed_movie_options = self.addon.getLocalizedString(32019)

        lines = [str_remove, str_move_back_to_staged, str_back]
        ret = xbmcgui.Dialog().select('{0} - {1} - {2}'.format(self.str_addon_name, str_managed_movie_options, item.get_title()), lines)
        if not ret<0:
            if lines[ret] == str_remove:
                item.remove_from_library()
                return self.view_managed_movies()
            elif lines[ret] == str_move_back_to_staged:
                item.add_to_staged_file()
                item.remove_from_library()
                return self.view_managed_movies()
            elif lines[ret] == str_back:
                return self.view_managed_movies()
        else:
            return self.view_managed_movies()

    def view_managed_tvshows(self):
        str_no_managed_tv_shows = self.addon.getLocalizedString(32020)
        str_remove_all_tv_shows = self.addon.getLocalizedString(32021)
        str_move_all_tv_shows_back_to_staged = self.addon.getLocalizedString(32022)
        str_back = self.addon.getLocalizedString(32011)
        str_managed_tv_shows = self.addon.getLocalizedString(32023)

        managed_items = get_items('managed.pkl')
        managed_tvshows = [x.get_show_title() for x in managed_items if x.get_mediatype()=='tvshow']
        if len(managed_tvshows)==0:
            xbmcgui.Dialog().ok(self.str_addon_name, str_no_managed_tv_shows)
            return self.choose_action()
        managed_tvshows = sorted(list(set(managed_tvshows)), key=str.lower)
        lines = ['[B]%s[/B]' % x for x in managed_tvshows]
        lines += [str_remove_all_tv_shows, str_move_all_tv_shows_back_to_staged, str_back]
        ret = xbmcgui.Dialog().select('{0} - {1}'.format(self.str_addon_name, str_managed_tv_shows), lines)
        if not ret<0:
            if ret<len(managed_tvshows):
                for show_title in managed_tvshows:
                    if managed_tvshows[ret]==show_title:
                        self.view_managed_tvshow_items(show_title)
            elif lines[ret] == str_remove_all_tv_shows:
                self.remove_all_managed_tvshows()
                return self.choose_action()
            elif lines[ret] == str_move_all_tv_shows_back_to_staged:
                self.move_all_managed_tvshows_to_staged()
                return self.choose_action()
            elif lines[ret] == str_back:
                return self.choose_action()
        else:
            self.choose_action()

    def remove_all_managed_tvshows(self):
        str_removing_all_tv_shows = self.addon.getLocalizedString(32024)
        str_all_tv_shows_removed = self.addon.getLocalizedString(32025)

        pDialog = xbmcgui.DialogProgress()
        pDialog.create(self.str_addon_name, str_removing_all_tv_shows)
        managed_items = get_items('managed.pkl')
        for item in managed_items:
            if item.get_mediatype()=='tvshow':
                pDialog.update(0,line2=item.get_show_title(),line3=item.get_title())
                item.remove_from_library()
            else:
                pDialog.update(0,line2=' ', line3=' ')
        pDialog.close()
        xbmc.executebuiltin('Notification("{0}", "{1}")'.format(self.str_addon_name, str_all_tv_shows_removed))

    def move_all_managed_tvshows_to_staged(self):
        str_moving_all_tv_shows_back_to_staged = self.addon.getLocalizedString(32026)
        str_all_tv_shows_moved_to_staged = self.addon.getLocalizedString(32027)

        pDialog = xbmcgui.DialogProgress()
        pDialog.create(self.str_addon_name, str_moving_all_tv_shows_back_to_staged)
        managed_items = get_items('managed.pkl')
        for item in managed_items:
            if item.get_mediatype()=='tvshow':
                pDialog.update(0,line2=item.get_show_title(),line3=item.get_title())
                item.add_to_staged_file()
                item.remove_from_library()
            else:
                pDialog.update(0,line2=' ', line3=' ')
        pDialog.close()
        xbmc.executebuiltin('Notification("{0}", "{1}")'.format(self.str_addon_name, str_all_tv_shows_moved_to_staged))

    def view_managed_tvshow_items(self, show_title):
        str_no_managed_x_episodes = self.addon.getLocalizedString(32028) % show_title
        str_remove_all_episodes = self.addon.getLocalizedString(32029)
        str_move_all_episodes_back_to_staged = self.addon.getLocalizedString(32030)
        str_back = self.addon.getLocalizedString(32011)
        str_managed_x_episodes = self.addon.getLocalizedString(32031) % show_title

        managed_items = get_items('managed.pkl')
        managed_episodes = [x for x in managed_items if x.get_mediatype()=='tvshow' and x.get_show_title()==show_title]
        if len(managed_episodes)==0:
            xbmcgui.Dialog().ok(self.str_addon_name, str_no_managed_x_episodes)
            return self.view_managed_tvshows()
        lines = [str(x) for x in managed_episodes]
        lines, managed_episodes = (list(t) for t in zip(*sorted(zip(lines, managed_episodes), key=lambda x: x[0].lower())))
        lines += [str_remove_all_episodes, str_move_all_episodes_back_to_staged, str_back]
        ret = xbmcgui.Dialog().select('{0} - {1}'.format(self.str_addon_name, str_managed_x_episodes), lines)
        if not ret<0:
            if ret<len(managed_episodes):   # managed item
                for i, item in enumerate(managed_episodes):
                    if ret==i:
                        self.managed_episode_options(item)
            elif lines[ret] == str_remove_all_episodes:
                self.remove_managed_episodes(show_title)
                return self.view_managed_tvshows()
            elif lines[ret] == str_move_all_episodes_back_to_staged:
                self.move_managed_episodes_to_staged(show_title)
                return self.view_managed_tvshows()
            elif lines[ret] == str_back:
                return self.view_managed_tvshows()
        else:
            self.view_managed_tvshows()

    def remove_managed_episodes(self, show_title):
        str_removing_all_x_episodes = self.addon.getLocalizedString(32032) % show_title
        str_all_x_episodes_removed = self.addon.getLocalizedString(32033) % show_title

        pDialog = xbmcgui.DialogProgress()
        pDialog.create(self.str_addon_name, str_removing_all_x_episodes)
        managed_items = get_items('managed.pkl')
        for item in managed_items:
            if item.get_mediatype()=='tvshow' and item.get_show_title()==show_title:
                pDialog.update(0,line2=item.get_title())
                item.remove_from_library()
            else:
                pDialog.update(0,line2=' ')
        pDialog.close()
        xbmc.executebuiltin('Notification("{0}", "{1}")'.format(self.str_addon_name, str_all_x_episodes_removed))

    def move_managed_episodes_to_staged(self, show_title):
        str_moving_all_x_episodes_back_to_staged = self.addon.getLocalizedString(32034) % show_title
        str_all_x_episodes_moved_to_staged = self.addon.getLocalizedString(32035) % show_title

        pDialog = xbmcgui.DialogProgress()
        pDialog.create(self.str_addon_name, str_moving_all_x_episodes_back_to_staged)
        managed_items = get_items('managed.pkl')
        for item in managed_items:
            if item.get_mediatype()=='tvshow' and item.get_show_title()==show_title:
                pDialog.update(0,line2=item.get_title())
                item.add_to_staged_file()
                item.remove_from_library()
            else:
                pDialog.update(0,line2=' ')
        pDialog.close()
        xbmc.executebuiltin('Notification("{0}", "{1}")'.format(self.str_addon_name, str_all_x_episodes_moved_to_staged))

    def managed_episode_options(self, item):
        str_remove = self.addon.getLocalizedString(32017)
        str_move_back_to_staged = self.addon.getLocalizedString(32018)
        str_back = self.addon.getLocalizedString(32011)
        str_managed_episode_options = self.addon.getLocalizedString(32036)

        lines = [str_remove, str_move_back_to_staged, str_back]
        ret = xbmcgui.Dialog().select('{0} - {1} - {2}'.format(self.str_addon_name, str_managed_episode_options, item.get_title()), lines)
        if not ret<0:
            if lines[ret] == str_remove:
                item.remove_from_library()
                return self.view_managed_tvshow_items(item.get_show_title())
            elif lines[ret] == str_move_back_to_staged:
                item.add_to_staged_file()
                item.remove_from_library()
                return self.view_managed_tvshow_items(item.get_show_title())
            elif lines[ret] == str_back:
                return self.view_managed_tvshow_items(item.get_show_title())
        else:
            return self.view_managed_tvshow_items(item.get_show_title())

    def view_staged_movies(self):
        str_no_staged_movies = self.addon.getLocalizedString(32037)
        str_add_all_movies = self.addon.getLocalizedString(32038)
        str_add_all_movies_with_metadata = self.addon.getLocalizedString(32039)
        str_remove_all_movies = self.addon.getLocalizedString(32009)
        str_generate_all_metadata_items = self.addon.getLocalizedString(32040)
        str_back = self.addon.getLocalizedString(32011)
        str_staged_movies = self.addon.getLocalizedString(32041)

        staged_items = get_items('staged.pkl')
        staged_movies = [x for x in staged_items if x.get_mediatype()=='movie']
        if len(staged_movies)==0:
            xbmcgui.Dialog().ok(self.str_addon_name, str_no_staged_movies)
            return self.choose_action()
        lines = [str(x) for x in staged_movies]
        lines, staged_movies = (list(t) for t in zip(*sorted(zip(lines, staged_movies), key=lambda x: x[0].lower())))
        lines += [str_add_all_movies, str_add_all_movies_with_metadata, str_remove_all_movies, str_generate_all_metadata_items, str_back]
        ret = xbmcgui.Dialog().select('{0} - {1}'.format(self.str_addon_name, str_staged_movies), lines)
        if not ret<0:
            if ret<len(staged_movies):   # staged item
                for i, item in enumerate(staged_movies):
                    if ret==i:
                        self.staged_movie_options(item)
            elif lines[ret] == str_add_all_movies:
                self.add_all_staged_movies()
            elif lines[ret] == str_add_all_movies_with_metadata:
                self.add_all_movies_with_metadata()
            elif lines[ret] == str_remove_all_movies:
                self.remove_all_staged_movies()
            elif lines[ret] == str_generate_all_metadata_items:
                self.generate_all_movie_metadata()
                return self.view_staged_movies()
            elif lines[ret] == str_back:
                self.choose_action()
        else:
            self.choose_action()

    def add_all_staged_movies(self):
        str_adding_all_movies = self.addon.getLocalizedString(32042)
        str_all_movies_added = self.addon.getLocalizedString(32043)

        pDialog = xbmcgui.DialogProgress()
        pDialog.create(self.str_addon_name, str_adding_all_movies)
        staged_items = get_items('staged.pkl')
        for item in staged_items:
            if item.get_mediatype()=='movie':
                pDialog.update(0,line2=item.get_title())
                item.add_to_library()
            else:
                pDialog.update(0,line2=' ')
        pDialog.close()
        xbmc.executebuiltin('Notification("{0}", "{1}")'.format(self.str_addon_name, str_all_movies_added))

    def add_all_movies_with_metadata(self):
        str_adding_all_movies_with_metadata = self.addon.getLocalizedString(32044)
        str_all_movies_with_metadata_added = self.addon.getLocalizedString(32045)

        pDialog = xbmcgui.DialogProgress()
        pDialog.create(self.str_addon_name, str_adding_all_movies_with_metadata)
        staged_items = get_items('staged.pkl')
        for item in staged_items:
            if item.get_mediatype()=='movie':
                safe_title = clean(item.get_title())
                metadata_dir = os.path.join(managed_folder, 'Metadata', 'Movies', safe_title)
                nfo_path = os.path.join(metadata_dir, safe_title + '.nfo')
                if os.path.exists(nfo_path):
                    pDialog.update(0,line2=item.get_title())
                    item.add_to_library()
            pDialog.update(0,line2=' ')
        pDialog.close()
        xbmc.executebuiltin('Notification("{0}", "{1}")'.format(self.str_addon_name, str_all_movies_with_metadata_added))

    def remove_all_staged_movies(self):
        str_removing_all_movies = self.addon.getLocalizedString(32013)
        str_all_movies_removed = self.addon.getLocalizedString(32014)

        pDialog = xbmcgui.DialogProgress()
        pDialog.create(self.str_addon_name, str_removing_all_movies)
        staged_items = get_items('staged.pkl')
        for item in staged_items:
            if item.get_mediatype()=='movie':
                pDialog.update(0,line2=item.get_title())
                item.remove_from_staged()
            else:
                pDialog.update(0,line2=' ')
        pDialog.close()
        xbmc.executebuiltin('Notification("{0}", "{1}")'.format(self.str_addon_name, str_all_movies_removed))

    def generate_all_movie_metadata(self):
        str_generating_all_movie_metadata = self.addon.getLocalizedString(32046)
        str_all_movie_metadata_created = self.addon.getLocalizedString(32047)

        pDialog = xbmcgui.DialogProgress()
        pDialog.create(self.str_addon_name, str_generating_all_movie_metadata)
        staged_items = get_items('staged.pkl')
        for item in staged_items:
            if item.get_mediatype()=='movie':
                pDialog.update(0,line2=item.get_title())
                item.create_metadata_item()
            else:
                pDialog.update(0,line2=' ')
        pDialog.close()
        xbmc.executebuiltin('Notification("{0}", "{1}")'.format(self.str_addon_name, str_all_movie_metadata_created))

    def staged_movie_options(self, item):
        str_add = self.addon.getLocalizedString(32048)
        str_remove = self.addon.getLocalizedString(32017)
        str_remove_and_block = self.addon.getLocalizedString(32049)
        str_rename = self.addon.getLocalizedString(32050)
        str_automatically_rename_using_metadata = self.addon.getLocalizedString(32051)
        str_generate_metadata_item = self.addon.getLocalizedString(32052)
        str_staged_movie_options = self.addon.getLocalizedString(32053)

        lines = [str_add, str_remove, str_remove_and_block, str_rename, str_automatically_rename_using_metadata, str_generate_metadata_item]
        ret = xbmcgui.Dialog().select('{0} - {1} - {2}'.format(self.str_addon_name, str_staged_movie_options, item.get_title()), lines)
        if not ret<0:
            if lines[ret] == str_add:
                item.add_to_library()
            elif lines[ret] == str_remove:
                item.remove_from_staged()
            elif lines[ret] == str_remove_and_block:
                self.remove_and_block_movie(item)
            elif lines[ret] == str_rename:
                self.rename_staged_item(item)
                return self.staged_movie_options(item)
            elif lines[ret] == str_generate_metadata_item:
                item.create_metadata_item()
                return self.staged_movie_options(item)
            elif lines[ret] == str_automatically_rename_using_metadata:
                item.rename_using_metadata()
                return self.staged_movie_options(item)
        self.view_staged_movies()

    def remove_and_block_movie(self, item):
        #TODO: move to ContentItem method
        # add show title to blocked
        append_item('blocked.pkl', {'type':'movie', 'label':item.get_title()})
        # delete metadata items
        safe_title = clean(item.get_title())
        movie_dir = os.path.join(managed_folder, 'Metadata', 'Movies', safe_title)
        os.system('rm -r "%s"' % movie_dir)
        # remove from staged
        item.remove_from_staged()

    def view_staged_tvshows(self):
        str_no_staged_tv_shows = self.addon.getLocalizedString(32054)
        str_add_all_tv_shows = self.addon.getLocalizedString(32055)
        str_add_all_items_with_metadata = self.addon.getLocalizedString(32056)
        str_remove_all_tv_shows = self.addon.getLocalizedString(32057)
        str_generate_all_metadata_items = self.addon.getLocalizedString(32040)
        str_back = self.addon.getLocalizedString(32011)
        str_staged_tv_shows = self.addon.getLocalizedString(32058)

        staged_items = get_items('staged.pkl')
        staged_tvshows = [x.get_show_title() for x in staged_items if x.get_mediatype()=='tvshow']
        if len(staged_tvshows)==0:
            xbmcgui.Dialog().ok(self.str_addon_name, str_no_staged_tv_shows)
            return self.choose_action()
        staged_tvshows = sorted(list(set(staged_tvshows)), key=str.lower)
        lines = ['[B]%s[/B]' % x for x in staged_tvshows]
        lines += [str_add_all_tv_shows, str_add_all_items_with_metadata, str_remove_all_tv_shows, str_generate_all_metadata_items, str_back]
        ret = xbmcgui.Dialog().select('{0} - {1}'.format(self.str_addon_name, str_staged_tv_shows), lines)
        if not ret<0:
            if ret<len(staged_tvshows):   # staged item
                for show_title in staged_tvshows:
                    if staged_tvshows[ret]==show_title:
                        self.view_staged_tvshow_items(show_title)
            elif lines[ret] == str_add_all_tv_shows:
                self.add_all_staged_tvshows()
            elif lines[ret] == str_add_all_items_with_metadata:
                self.add_all_tvshows_with_metadata()
                return self.view_staged_tvshows()
            elif lines[ret] == str_remove_all_tv_shows:
                self.remove_all_staged_tvshows()
            elif lines[ret] == str_generate_all_metadata_items:
                self.generate_all_tvshow_metadata()
            elif lines[ret] == str_back:
                self.choose_action()
        else:
            self.choose_action()

    def add_all_staged_tvshows(self):
        str_adding_all_tv_shows = self.addon.getLocalizedString(32059)
        str_all_tv_shows_added = self.addon.getLocalizedString(32060)

        pDialog = xbmcgui.DialogProgress()
        pDialog.create(self.str_addon_name, str_adding_all_tv_shows)
        staged_items = get_items('staged.pkl')
        for item in staged_items:
            if item.get_mediatype()=='tvshow':
                pDialog.update(0,line2=item.get_title())
                item.add_to_library()
            else:
                pDialog.update(0,line2=' ')
        pDialog.close()
        xbmc.executebuiltin('Notification("{0}", "{1}")'.format(self.str_addon_name, str_all_tv_shows_added))

    def add_all_tvshows_with_metadata(self):
        str_adding_all_tv_show_items_with_metadata = self.addon.getLocalizedString(32061)
        str_all_tv_show_items_with_metadata_added = self.addon.getLocalizedString(32062)

        pDialog = xbmcgui.DialogProgress()
        pDialog.create(self.str_addon_name, str_adding_all_tv_show_items_with_metadata)
        staged_items = get_items('staged.pkl')
        for item in staged_items:
            if item.get_mediatype()=='tvshow':
                safe_title = clean(item.get_title())
                safe_showtitle = clean(item.get_show_title())
                metadata_dir = os.path.join(managed_folder, 'Metadata', 'TV', safe_showtitle)
                nfo_path = os.path.join(metadata_dir, safe_title + '.nfo')
                if os.path.exists(nfo_path):
                    pDialog.update(0,line2=item.get_show_title(),line3=item.get_title())
                    item.add_to_library()
            pDialog.update(0,line2=' ',line3=' ')
        pDialog.close()
        xbmc.executebuiltin('Notification("{0}", "{1}")'.format(self.str_addon_name, str_all_tv_show_items_with_metadata_added))

    def remove_all_staged_tvshows(self):
        str_removing_all_tv_shows = self.addon.getLocalizedString(32024)
        str_all_tv_shows_removed = self.addon.getLocalizedString(32025)

        pDialog = xbmcgui.DialogProgress()
        pDialog.create(self.str_addon_name, str_removing_all_tv_shows)
        staged_items = get_items('staged.pkl')
        for item in staged_items:
            if item.get_mediatype()=='tvshow':
                pDialog.update(0,line2=item.get_title())
                item.remove_from_staged()
            else:
                pDialog.update(0,line2=' ')
        pDialog.close()
        xbmc.executebuiltin('Notification("{0}", "{1}")'.format(self.str_addon_name, str_all_tv_shows_removed))

    def generate_all_tvshow_metadata(self):
        str_generating_all_tv_show_metadata = self.addon.getLocalizedString(32063)
        str_all_tv_show_metadata_created = self.addon.getLocalizedString(32064)

        pDialog = xbmcgui.DialogProgress()
        pDialog.create(self.str_addon_name, str_generating_all_tv_show_metadata)
        staged_items = get_items('staged.pkl')
        for item in staged_items:
            if item.get_mediatype()=='tvshow':
                pDialog.update(0,line2=item.get_show_title(),line3=item.get_title())
                item.create_metadata_item()
            else:
                pDialog.update(0,line2=' ',line3=' ')
        pDialog.close()
        xbmc.executebuiltin('Notification("{0}", "{1}")'.format(self.str_addon_name, str_all_tv_show_metadata_created))

    def view_staged_tvshow_items(self, show_title):
        str_no_staged_x_episodes = self.addon.getLocalizedString(32065) % show_title
        str_add_all_episodes = self.addon.getLocalizedString(32066)
        str_add_all_episodes_with_metadata = self.addon.getLocalizedString(32067)
        str_remove_all_episodes = self.addon.getLocalizedString(32029)
        str_remove_and_block_tv_show = self.addon.getLocalizedString(32068)
        str_automatically_rename_all_episodes_using_metadata = self.addon.getLocalizedString(32069)
        str_generate_all_metadata_items = self.addon.getLocalizedString(32040)
        str_back = self.addon.getLocalizedString(32011)
        str_staged_x_episodes = self.addon.getLocalizedString(32070) % show_title

        staged_items = get_items('staged.pkl')
        staged_episodes = [x for x in staged_items if x.get_mediatype()=='tvshow' and x.get_show_title()==show_title]
        if len(staged_episodes)==0:
            xbmcgui.Dialog().ok(self.str_addon_name, str_no_staged_x_episodes)
            return self.view_staged_tvshows()
        lines = [str(x) for x in staged_episodes]
        lines, staged_episodes = (list(t) for t in zip(*sorted(zip(lines, staged_episodes), key=lambda x: x[0].lower())))
        lines += [str_add_all_episodes, str_add_all_episodes_with_metadata, str_remove_all_episodes, str_remove_and_block_tv_show,
                    str_automatically_rename_all_episodes_using_metadata, str_generate_all_metadata_items, str_back]
        ret = xbmcgui.Dialog().select('{0} - {1}'.format(self.str_addon_name, str_staged_x_episodes), lines)
        if not ret<0:
            if ret<len(staged_episodes):   # staged item
                for i, item in enumerate(staged_episodes):
                    if ret==i:
                        self.staged_episode_options(item)
            elif lines[ret] == str_add_all_episodes:
                self.add_all_staged_episodes(show_title)
                return self.view_staged_tvshows()
            elif lines[ret] == str_add_all_episodes_with_metadata:
                self.add_all_tvshow_items_with_metadata(show_title)
                return self.view_staged_tvshow_items(show_title)
            elif lines[ret] == str_remove_all_episodes:
                self.remove_all_staged_episodes(show_title)
                return self.view_staged_tvshows()
            elif lines[ret] == str_remove_and_block_tv_show:
                self.remove_and_block_staged_tvshow(show_title)
                return self.view_staged_tvshows()
            elif lines[ret] == str_automatically_rename_all_episodes_using_metadata:
                self.rename_tvshow_using_metadata(show_title)
                return self.view_staged_tvshow_items(show_title)
            elif lines[ret] == str_generate_all_metadata_items:
                self.generate_all_episodes_metadata(show_title)
                return self.view_staged_tvshow_items(show_title)
            elif lines[ret] == str_back:
                self.view_staged_tvshows()
        else:
            self.view_staged_tvshows()

    def add_all_staged_episodes(self, show_title):
        str_adding_all_x_episodes = self.addon.getLocalizedString(32071) % show_title
        str_all_x_episodes_added = self.addon.getLocalizedString(32072) % show_title

        pDialog = xbmcgui.DialogProgress()
        pDialog.create(self.str_addon_name, str_adding_all_x_episodes)
        staged_items = get_items('staged.pkl')
        for item in staged_items:
            if item.get_mediatype()=='tvshow' and item.get_show_title()==show_title:
                pDialog.update(0,line2=item.get_title())
                item.add_to_library()
            else:
                pDialog.update(0,line2=' ')
        pDialog.close()
        xbmc.executebuiltin('Notification("{0}", "{1}")' % (self.str_addon_name, str_all_x_episodes_added))

    def add_all_tvshow_items_with_metadata(self, show_title):
        str_adding_all_x_episodes_with_metadata = self.addon.getLocalizedString(32073) % show_title
        str_all_x_episodes_with_metadata_added = self.addon.getLocalizedString(32074) % show_title


        pDialog = xbmcgui.DialogProgress()
        pDialog.create(self.str_addon_name, str_adding_all_x_episodes_with_metadata)
        staged_items = get_items('staged.pkl')
        for item in staged_items:
            if item.get_mediatype()=='tvshow' and item.get_show_title()==show_title:
                safe_title = clean(item.get_title())
                safe_showtitle = clean(show_title)
                metadata_dir = os.path.join(managed_folder, 'Metadata', 'TV', safe_showtitle)
                nfo_path = os.path.join(metadata_dir, safe_title + '.nfo')
                if os.path.exists(nfo_path):
                    pDialog.update(0,line2=show_title,line3=item.get_title())
                    item.add_to_library()
            pDialog.update(0,line2=' ',line3=' ')
        pDialog.close()
        xbmc.executebuiltin('Notification("{0}", "{1}")' % (self.str_addon_name, str_all_x_episodes_with_metadata_added))

    def remove_all_staged_episodes(self, show_title):
        str_removing_all_x_episodes = self.addon.getLocalizedString(32032) % show_title
        str_all_x_episodes_removed = self.addon.getLocalizedString(32033) % show_title

        pDialog = xbmcgui.DialogProgress()
        pDialog.create(self.str_addon_name, str_removing_all_x_episodes)
        staged_items = get_items('staged.pkl')
        for item in staged_items:
            if item.get_mediatype()=='tvshow' and item.get_show_title()==show_title:
                pDialog.update(0,line2=item.get_title())
                item.remove_from_staged()
            else:
                pDialog.update(0,line2=' ')
        pDialog.close()
        xbmc.executebuiltin('Notification("{0}", "{1}")' % (self.str_addon_name, str_all_x_episodes_removed))

    def remove_and_block_staged_tvshow(self, show_title):
        #TODO: move to ContentItem method
        # remove from staged
        self.remove_all_staged_episodes(show_title)
        # delete metadata folder
        safe_showtitle = clean(show_title)
        metadata_dir = os.path.join(managed_folder, 'Metadata', 'TV', safe_showtitle)
        os.system('rm -r "%s"' % metadata_dir)
        # add show title to blocked
        append_item('blocked.pkl', {'type':'show', 'label':show_title})

    def rename_tvshow_using_metadata(self, show_title):
        str_renaming_all_x_episodes_using_metadata = self.addon.getLocalizedString(32075) % show_title
        str_all_x_episodes_renamed_using_metadata = self.addon.getLocalizedString(32076) % show_title

        pDialog = xbmcgui.DialogProgress()
        pDialog.create(self.str_addon_name, str_renaming_all_x_episodes_using_metadata)
        staged_items = get_items('staged.pkl')
        for item in staged_items:
            if item.get_mediatype()=='tvshow' and item.get_show_title()==show_title:
                pDialog.update(0,line2=item.get_title())
                item.rename_using_metadata()
            else:
                pDialog.update(0,line2=' ')
        pDialog.close()
        xbmc.executebuiltin('Notification("{0}", "{1}")' % (self.str_addon_name, str_all_x_episodes_renamed_using_metadata))

    def generate_all_episodes_metadata(self, show_title):
        str_generating_all_x_metadata = self.addon.getLocalizedString(32077) % show_title
        str_all_x_metadata_created = self.addon.getLocalizedString(32078) % show_title

        pDialog = xbmcgui.DialogProgress()
        pDialog.create(self.str_addon_name, str_generating_all_x_metadata)
        staged_items = get_items('staged.pkl')
        for item in staged_items:
            if item.get_mediatype()=='tvshow' and item.get_show_title()==show_title:
                pDialog.update(0,line2=item.get_title())
                item.create_metadata_item()
            else:
                pDialog.update(0,line2=' ')
        pDialog.close()
        xbmc.executebuiltin('Notification("{0}", {1}")' % (self.str_addon_name, str_all_x_metadata_created))

    def staged_episode_options(self, item):
        #TODO: rename associated metadata when renaming
        #TODO: change item.show_title to item.get_show_title after I've rebuilt library
        #TODO: automatically rename based on nfo file for all items in tv show
        #TODO: rename show title
        #TODO: add to blocked movies/shows
        #TODO: remove item (including metadata)
        str_add = self.addon.getLocalizedString(32048)
        str_remove = self.addon.getLocalizedString(32017)
        str_remove_and_block_episode = self.addon.getLocalizedString(32079)
        str_rename = self.addon.getLocalizedString(32050)
        str_automatically_rename_using_metadata = self.addon.getLocalizedString(32051)
        str_generate_metadata_item = self.addon.getLocalizedString(32052)
        str_back = self.addon.getLocalizedString(32011)
        str_staged_episode_options = self.addon.getLocalizedString(32080)

        lines = [str_add, str_remove, str_remove_and_block_episode, str_rename, str_automatically_rename_using_metadata, str_generate_metadata_item, str_back]
        ret = xbmcgui.Dialog().select('{0} - {1} - {2}'.format(self.str_addon_name, str_staged_episode_options, item.get_title()), lines)
        if not ret<0:
            if lines[ret] == str_add:
                item.add_to_library()
                return self.view_staged_tvshow_items(item.get_show_title())
            elif lines[ret] == str_remove:
                item.remove_from_staged()
                return self.view_staged_tvshow_items(item.get_show_title())
            elif lines[ret] == str_remove_and_block_episode:
                self.remove_and_block_episode(item)
                return self.view_staged_tvshow_items(item.get_show_title())
            elif lines[ret] == str_rename:
                self.rename_staged_item(item)
                return self.staged_episode_options(item)
            elif lines[ret] == str_generate_metadata_item:
                item.create_metadata_item()
                return self.staged_episode_options(item)
            elif lines[ret] == str_automatically_rename_using_metadata:
                item.rename_using_metadata()
                return self.staged_episode_options(item)
            elif lines[ret] == str_back:
                return self.view_staged_tvshow_items(item.get_show_title())
        else:
            self.view_staged_tvshow_items(item.get_show_title())

    def remove_and_block_episode(self, item):
        # TODO: remove replace('-0x0') and make blocked episode matching 'in' not '=='
        # TODO: move to ContentItem method
        # add show title to blocked
        append_item('blocked.pkl', {'type':'episode', 'label':item.get_title().replace('-0x0','')})
        # delete metadata items
        safe_showtitle = clean(item.get_show_title())
        safe_title = clean(item.get_title())
        title_path = os.path.join(managed_folder, 'Metadata', 'TV', safe_showtitle, safe_title)
        os.system('rm "%s"*' % title_path)
        # remove from staged
        item.remove_from_staged()

    def rename_staged_item(self, item):
        input_ret = xbmcgui.Dialog().input("Title", defaultt=item.title)
        if input_ret:
            item.rename(input_ret)

    def view_synced(self):
        #TODO: localization for mediatype
        #?TODO: class for synced directories
        str_update_all = self.addon.getLocalizedString(32081)
        str_remove_all = self.addon.getLocalizedString(32082)
        str_back = self.addon.getLocalizedString(32011)
        str_synced_directories = self.addon.getLocalizedString(32011)

        synced_dirs = get_items('synced.pkl')
        lines = ['%ss - [I]%s[/I]'%(x['mediatype'], x['dir']) for x in synced_dirs]
        lines += [str_update_all, str_remove_all, str_back]
        ret = xbmcgui.Dialog().select('{0} - {1}'.format(self.str_addon_name, str_synced_directories), lines)
        if not ret<0:
            if ret<len(synced_dirs):   # managed item
                for i, x in enumerate(synced_dirs):
                    if ret==i:
                        self.synced_dir_options(x)
            elif lines[ret] == str_update_all:
                self.update_all_synced(synced_dirs)
            elif lines[ret] == str_remove_all:
                self.remove_all_synced()
            elif lines[ret] == str_back:
                self.choose_action()
        else:
            self.choose_action()

    def synced_dir_options(self, item):
        #TODO: remove all from plugin
        str_update = self.addon.getLocalizedString(32084)
        str_remove = self.addon.getLocalizedString(32017)
        str_synced_directory_options = self.addon.getLocalizedString(32085)

        lines = [str_update, str_remove]
        ret = xbmcgui.Dialog().select('{0} - {1} - {2}' % (self.str_addon_name, str_synced_directory_options, item['dir']), lines)
        if not ret<0:
            if lines[ret] == str_update:
                self.update_synced_dir(item)
            elif lines[ret] == str_remove:
                remove_item('synced.pkl', item)
        self.view_synced()

    def remove_all_synced(self):
        str_remove_all_synced_directories = self.addon.getLocalizedString(32086)
        str_all_synced_directories_removed = self.addon.getLocalizedString(32087)
        str_are_you_sure = self.addon.getLocalizedString(32088)

        if xbmcgui.Dialog().yesno('{0} - {1}'.format(self.str_addon_name, str_remove_all_synced_directories), str_are_you_sure):
            save_items('synced.pkl', [])
            xbmc.executebuiltin('Notification("{0}", "{1}")'.format(self.str_addon_name, str_all_synced_directories_removed))

    def update_synced_dir(self, item):
        # TODO: allow updating individual directories
        pass

    def update_all_synced(self, synced_dirs):
        #TODO: make it so manually added items don't just get deleted
        #   (need to add 'single-movie' and 'single-tvshow' mediatype that gets checked in 'getting all...')
        #TODO: don't initialize ContentItem until after confirmation
        #TODO: should move blocked check up to 'getting all items from ...'
        #TODO: move out of main
        str_getting_all_items_from_synced_directories = self.addon.getLocalizedString(32089)
        str_finding_items_to_remove_from_managed = self.addon.getLocalizedString(32090)
        str_removing_items_from_staged = self.addon.getLocalizedString(32091)
        str_finding_items_to_add = self.addon.getLocalizedString(32092)
        str_i_items_to_remove_i_items_to_stage_proceed = self.addon.getLocalizedString(32093)
        str_removing_items = self.addon.getLocalizedString(32094)
        str_staging_items = self.addon.getLocalizedString(32095)
        str_all_synced_directories_updated = self.addon.getLocalizedString(32095)

        pDialog = xbmcgui.DialogProgress()
        pDialog.create(self.str_addon_name)

        # get current items in all directories
        pDialog.update(0, line1 = str_getting_all_items_from_synced_directories)
        dir_items = []
        for synced_dir in synced_dirs:
            pDialog.update(0, line2=synced_dir['dir'])
            result = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Files.GetDirectory", "params": {"directory":"%s"}, "id": 1}' % synced_dir['dir'])
            synced_dir_items = json.loads(result)["result"]["files"]
            if synced_dir['mediatype']=='movie':
                for ditem in synced_dir_items:
                    ditem['mediatype'] = 'movie'
                dir_items += synced_dir_items
            elif synced_dir['mediatype']=='tvshow':
                for ditem in synced_dir_items:
                    show_title = ditem['label']
                    pDialog.update(0, line3 = show_title)
                    show_path = ditem['file']
                    show_result = json.loads(xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Files.GetDirectory", "params": {"directory":"%s"}, "id": 1}' % show_path))
                    if not (show_result.has_key('result') and show_result["result"].has_key('files')):
                        pDialog.update(0, line3=' ')
                        continue
                    show_items = show_result["result"]["files"]
                    for shitem in show_items:
                        shitem['mediatype'] = 'tvshow'
                        shitem['show_title'] = show_title
                    dir_items += show_items
                    pDialog.update(0, line3=' ')
            pDialog.update(0, line2=' ')

        # find managed_items not in dir_items, and prepare to remove
        pDialog.update(0, line1 = str_finding_items_to_remove_from_managed)
        managed_items = get_items('managed.pkl')
        dir_paths = [x['file'] for x in dir_items]
        items_to_remove = []
        for item in managed_items:
            if item.get_path() not in dir_paths:
                pDialog.update(0, line2=item.get_title())
                items_to_remove.append(item)
            pDialog.update(0, line2=' ')


        # remove them from staged also (can do that immediately)
        pDialog.update(0, line1 = str_removing_items_from_staged)
        staged_items = get_items('staged.pkl')
        for item in staged_items:
            if item.get_path() not in dir_paths:
                pDialog.update(0, line2=item.get_title())
                item.remove_from_staged()
            pDialog.update(0, line2=' ')

        # find dir_items not in managed_items or staged_items, and prepare to add
        pDialog.update(0, line1 = str_finding_items_to_add)
        managed_paths = [x.get_path() for x in managed_items]
        staged_items = get_items('staged.pkl')
        staging_paths = [x.get_path() for x in staged_items]
        blocked_items = get_items('blocked.pkl')
        blocked_movies = [x['label'] for x in blocked_items if x['type']=='movie']
        blocked_episodes = [x['label'] for x in blocked_items if x['type']=='episode']
        blocked_shows = [x['label'] for x in blocked_items if x['type']=='show']
        blocked_keywords = [x['label'].lower() for x in blocked_items if x['type']=='keyword']
        items_to_stage = []
        for ditem in dir_items:
            label = ditem['label']
            path = ditem['file']
            pDialog.update(0, line2=label)
            if path in managed_paths or path in staging_paths:
                continue
            elif any(x in label.lower() for x in blocked_keywords):
                continue
            elif ditem['mediatype']=='movie' and label in blocked_movies:
                continue
            elif ditem['mediatype']=='tvshow' and ((label in blocked_episodes) or (ditem['show_title'] in blocked_shows)):
                continue
            if ditem['mediatype']=='movie':
                item = MovieItem(ditem['file'], ditem['label'], ditem['mediatype'])
            elif ditem['mediatype']=='tvshow':
                item = EpisodeItem(ditem['file'], ditem['label'], ditem['mediatype'], ditem['show_title'])
            items_to_stage.append(item)
            staging_paths.append(ditem['file'])
        pDialog.update(0, line2=' ')

        # prompt user to remove & stage
        num_to_remove = len(items_to_remove)
        num_to_stage = len(items_to_stage)
        if num_to_remove>0 or num_to_stage>0:
            proceed = xbmcgui.Dialog().yesno(self.str_addon_name, str_i_items_to_remove_i_items_to_stage_proceed % (num_to_remove,num_to_stage))
            if proceed:
                pDialog.update(0, line1 = str_removing_items)
                for item in items_to_remove:
                    log_msg('Removing from library: %s' % item.get_title(), xbmc.LOGNOTICE)
                    pDialog.update(0, line2=item.get_title())
                    item.remove_from_library()
                    pDialog.update(0, line2=' ')
                pDialog.update(0, line1 = str_staging_items)
                if num_to_stage>0:
                    staged_items += items_to_stage
                    save_items('staged.pkl',staged_items)
                    log_msg('Updated staged file with items from synced directories.', xbmc.LOGNOTICE)
                if num_to_remove>0:
                    xbmc.executebuiltin('CleanLibrary("video")')
                xbmc.executebuiltin('Notification("{0}", "{1}")'.format(self.str_addon_name, str_all_synced_directories_updated))
        pDialog.close()

    def view_blocked(self):
        #?TODO: change movie/episode to just path
        #?TODO: make blocked episode match on episode & show
        #TODO: add types: plugin, path
        str_add_keyword = self.addon.getLocalizedString(32097)
        str_back = self.addon.getLocalizedString(32011)
        str_blocked_items = self.addon.getLocalizedString(32098)

        blocked_items = get_items('blocked.pkl')
        lines = ['[B]%s[/B] - %s' % (x['label'], localize_mediatype(x['type'])) for x in blocked_items]
        lines, blocked_items = (list(t) for t in zip(*sorted(zip(lines, blocked_items), key=lambda x: x[0].lower())))
        lines += [str_add_keyword, str_back]
        ret = xbmcgui.Dialog().select('{0} - {1}'.format(self.str_addon_name, str_blocked_items), lines)
        if not ret<0:
            if ret<len(blocked_items):   # managed item
                for i, x in enumerate(blocked_items):
                    if ret==i:
                        self.blocked_item_options(x)
            elif lines[ret] == str_add_keyword:
                self.add_blocked_keyword()
                return self.view_blocked()
            elif lines[ret] == str_back:
                self.choose_action()
        else:
            self.choose_action()

    def add_blocked_keyword(self):
        input_ret = xbmcgui.Dialog().input("Blocked keyword")
        if input_ret:
            append_item('blocked.pkl', {'type':'keyword', 'label':input_ret})

    def blocked_item_options(self, item):
        str_remove = self.addon.getLocalizedString(32017)
        str_back = self.addon.getLocalizedString(32011)
        str_blocked_item_options = self.addon.getLocalizedString(32099)

        lines = [str_remove, str_back]
        ret = xbmcgui.Dialog().select('{0} - {1} - {2}'.format(self.str_addon_name, str_blocked_item_options, item['label']), lines)
        if not ret<0:
            if lines[ret] == str_remove:
                remove_item('blocked.pkl', item)
                return self.view_blocked()
            elif lines[ret] == str_back:
                self.view_blocked()
        self.view_blocked()
