#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import cPickle as pickle
import simplejson as json
import xbmc
import xbmcgui

from contentitem import MovieItem, EpisodeItem
from utils import log_msg, get_items, save_items, append_item, remove_item, clean

managed_folder = '/Volumes/Drobo Media/LibraryTools/'

class Main(object):
    #TODO: use staticmethod tag and maybe move some methods to utils
    #TODO: define strings here (and eventually localize)
    #TODO: use sqlite database... will lead to LOTS of optimizations
    #TODO: unit tests
    #TODO: pass around a 'previous view' function handle

    def __init__(self):
        self.choose_action()

    def choose_action(self):
        #TODO: new "View blocked items", with blocked keywords and shows/movies
        #TODO: fix update library to only update path
        #TODO: view by show title
        #TODO: remove extraneous tv show folders in Metadata
        #TODO: add all items with metadata
        #?TODO: add all from here
        #?TODO: view all
        #TODO: rebuild managed list (remove all items, then re-add new instance of ContentItem)
        #TODO: add parameter for location in list - useful when returning here after doing something on an item (preselct is broken when pressing cancel)
        lines = ["View Managed Movies", "View Managed TV Shows", "View Staged Movies", "View Staged TV Shows",
            "View Synced Directories", "View Blocked Items", "Update Library", "Clean Library"]
        ret = xbmcgui.Dialog().select('Library Integration Tool', lines)
        if not ret<0:
            if lines[ret]=='View Managed Movies':
                self.view_managed_movies()
            elif lines[ret]=='View Managed TV Shows':
                self.view_managed_tvshows()
            elif lines[ret]=='View Staged Movies':
                self.view_staged_movies()
            elif lines[ret]=='View Staged TV Shows':
                self.view_staged_tvshows()
            elif lines[ret]=='View Synced Directories':
                self.view_synced()
            elif lines[ret]=='View Blocked Items':
                self.view_blocked()
            elif lines[ret]=='Update Library':
                xbmc.executebuiltin('UpdateLibrary("video")')
                #xbmc.executebuiltin('UpdateLibrary("video, %s")' % managed_folder+'ManagedTV/')     #not working yet
                #xbmc.executebuiltin('UpdateLibrary("video, %s")' % managed_folder+'ManagedMovies/')
            elif lines[ret]=='Clean Library':
                xbmc.executebuiltin('CleanLibrary("video")')

    def view_managed_movies(self):
        managed_items = get_items('managed.pkl')
        managed_movies = [x for x in managed_items if x.get_mediatype()=='movie']
        if len(managed_movies)==0:
            xbmcgui.Dialog().ok('Library Integration Tool', 'No managed movies')
            return self.choose_action()
        lines = [str(x) for x in managed_movies]
        lines, managed_movies = (list(t) for t in zip(*sorted(zip(lines, managed_movies))))
        lines += ["Remove all movies", "Move all items back to staged", "Back..."]
        ret = xbmcgui.Dialog().select('Library Integration Tool - Managed Movies', lines)
        if not ret<0:
            if ret<len(managed_movies):   # managed item
                for i, item in enumerate(managed_movies):
                    if ret==i:
                        self.managed_movie_options(item)
            elif lines[ret]=='Remove all items':
                self.remove_all_managed_movies()
                return self.choose_action()
            elif lines[ret]=='Move all items back to staged':
                self.move_all_managed_movies_to_staged()
                return self.choose_action()
            elif lines[ret]=='Back...':
                return self.choose_action()
        else:
            self.choose_action()

    def remove_all_managed_movies(self):
        pDialog = xbmcgui.DialogProgress()
        pDialog.create('Library Integration Tool', 'Removing all movies...')
        managed_items = get_items('managed.pkl')
        for item in managed_items:
            if item.get_mediatype()=='movie':
                pDialog.update(0,line2=item.get_title())
                item.remove_from_library()
            else:
                pDialog.update(0,line2=' ')
        pDialog.close()
        xbmc.executebuiltin("Notification(\"Library Integration Tool\", \"All movies removed\")")

    def move_all_managed_movies_to_staged(self):
        pDialog = xbmcgui.DialogProgress()
        pDialog.create('Library Integration Tool', 'Moving all movies back to staged...')
        managed_items = get_items('managed.pkl')
        for item in managed_items:
            if item.get_mediatype()=='movie':
                pDialog.update(0,line2=item.get_title())
                item.add_to_staged_file()
                item.remove_from_library()
            else:
                pDialog.update(0,line2=' ')
        pDialog.close()
        xbmc.executebuiltin("Notification(\"Library Integration Tool\", \"All movies moved to staged\")")

    def managed_movie_options(self, item):
        # TODO: add rename option
        # TODO: add reload metadata option
        # TODO: move back to staging
        # TODO: change item.show_title to item.get_show_title after I've rebuilt library
        lines = ["Remove", "Move back to staged", "Back..."]
        ret = xbmcgui.Dialog().select('Library Integration Tool - Managed Movie Options - %s' % item.get_title(), lines)
        if not ret<0:
            if lines[ret]=='Remove':
                item.remove_from_library()
                return self.view_managed_movies()
            elif lines[ret]=='Move back to staged':
                item.add_to_staged_file()
                item.remove_from_library()
                return self.view_managed_movies()
            elif lines[ret]=='Back...':
                return self.view_managed_movies()
        else:
            return self.view_managed_movies()

    def view_managed_tvshows(self):
        managed_items = get_items('managed.pkl')
        managed_tvshows = [x.get_show_title() for x in managed_items if x.get_mediatype()=='tvshow']
        if len(managed_tvshows)==0:
            xbmcgui.Dialog().ok('Library Integration Tool', 'No managed TV shows')
            return self.choose_action()
        managed_tvshows = sorted(list(set(managed_tvshows)))
        lines = ['[B]%s[/B]' % x for x in managed_tvshows]
        lines += ["Remove all TV shows", "Move all TV shows back to staged", "Back..."]
        ret = xbmcgui.Dialog().select('Library Integration Tool - Managed TV Shows', lines)
        if not ret<0:
            if ret<len(managed_tvshows):
                for show_title in managed_tvshows:
                    if managed_tvshows[ret]==show_title:
                        self.view_managed_tvshow_items(show_title)
            elif lines[ret]=='Remove all TV shows':
                self.remove_all_managed_tvshows()
                return self.choose_action()
            elif lines[ret]=='Move all TV shows back to staged':
                self.move_all_managed_tvshows_to_staged()
                return self.choose_action()
            elif lines[ret]=='Back...':
                return self.choose_action()
        else:
            self.choose_action()

    def remove_all_managed_tvshows(self):
        pDialog = xbmcgui.DialogProgress()
        pDialog.create('Library Integration Tool', 'Removing all TV shows...')
        managed_items = get_items('managed.pkl')
        for item in managed_items:
            if item.get_mediatype()=='tvshow':
                pDialog.update(0,line2=item.get_show_title(),line3=item.get_title())
                item.remove_from_library()
            else:
                pDialog.update(0,line2=' ', line3=' ')
        pDialog.close()
        xbmc.executebuiltin("Notification(\"Library Integration Tool\", \"All TV shows removed\")")

    def move_all_managed_tvshows_to_staged(self):
        pDialog = xbmcgui.DialogProgress()
        pDialog.create('Library Integration Tool', 'Moving all TV shows back to staged...')
        managed_items = get_items('managed.pkl')
        for item in managed_items:
            if item.get_mediatype()=='tvshow':
                pDialog.update(0,line2=item.get_show_title(),line3=item.get_title())
                item.add_to_staged_file()
                item.remove_from_library()
            else:
                pDialog.update(0,line2=' ', line3=' ')
        pDialog.close()
        xbmc.executebuiltin("Notification(\"Library Integration Tool\", \"All TV shows moved to staged\")")

    def view_managed_tvshow_items(self, show_title):
        managed_items = get_items('managed.pkl')
        managed_episodes = [x for x in managed_items if x.get_mediatype()=='tvshow' and x.get_show_title()==show_title]
        if len(managed_episodes)==0:
            xbmcgui.Dialog().ok('Library Integration Tool', 'No managed %s episodes' % show_title)
            return self.view_managed_tvshows()
        lines = [str(x) for x in managed_episodes]
        lines, managed_episodes = (list(t) for t in zip(*sorted(zip(lines, managed_episodes))))
        lines += ["Remove all episodes", "Move all episodes back to staged", "Back..."]
        ret = xbmcgui.Dialog().select('Library Integration Tool - Managed %s Episodes' % show_title, lines)
        if not ret<0:
            if ret<len(managed_episodes):   # managed item
                for i, item in enumerate(managed_episodes):
                    if ret==i:
                        self.managed_episode_options(item)
            elif lines[ret]=='Remove all episodes':
                self.remove_managed_episodes(show_title)
                return self.view_managed_tvshows()
            elif lines[ret]=='Move all episodes back to staged':
                self.move_managed_episodes_to_staged(show_title)
                return self.view_managed_tvshows()
            elif lines[ret]=='Back...':
                return self.view_managed_tvshows()
        else:
            self.view_managed_tvshows()

    def remove_managed_episodes(self, show_title):
        pDialog = xbmcgui.DialogProgress()
        pDialog.create('Library Integration Tool', 'Removing all episodes...')
        managed_items = get_items('managed.pkl')
        for item in managed_items:
            if item.get_mediatype()=='tvshow' and item.get_show_title()==show_title:
                pDialog.update(0,line2=item.get_title())
                item.remove_from_library()
            else:
                pDialog.update(0,line2=' ')
        pDialog.close()
        xbmc.executebuiltin("Notification(\"Library Integration Tool\", \"All TV shows removed\")")

    def move_managed_episodes_to_staged(self, show_title):
        pDialog = xbmcgui.DialogProgress()
        pDialog.create('Library Integration Tool', 'Moving all episodes back to staged...')
        managed_items = get_items('managed.pkl')
        for item in managed_items:
            if item.get_mediatype()=='tvshow' and item.get_show_title()==show_title:
                pDialog.update(0,line2=item.get_title())
                item.add_to_staged_file()
                item.remove_from_library()
            else:
                pDialog.update(0,line2=' ')
        pDialog.close()
        xbmc.executebuiltin("Notification(\"Library Integration Tool\", \"All episodes moved to staged\")")

    def managed_episode_options(self, item):
        lines = ["Remove", "Move back to staged", "Back..."]
        ret = xbmcgui.Dialog().select('Library Integration Tool - Managed Episode Options - %s' % item.get_title(), lines)
        if not ret<0:
            if lines[ret]=='Remove':
                item.remove_from_library()
                return self.view_managed_tvshow_items(item.get_show_title())
            elif lines[ret]=='Move back to staged':
                item.add_to_staged_file()
                item.remove_from_library()
                return self.view_managed_tvshow_items(item.get_show_title())
            elif lines[ret]=='Back...':
                return self.view_managed_tvshow_items(item.get_show_title())
        else:
            return self.view_managed_tvshow_items(item.get_show_title())

    def view_staged_movies(self):
        staged_items = get_items('staged.pkl')
        staged_movies = [x for x in staged_items if x.get_mediatype()=='movie']
        if len(staged_movies)==0:
            xbmcgui.Dialog().ok('Library Integration Tool', 'No staged movies')
            return self.choose_action()
        lines = [str(x) for x in staged_movies]
        lines, staged_movies = (list(t) for t in zip(*sorted(zip(lines, staged_movies))))
        lines += ["Add all movies", "Add all movies with metadata", "Remove all movies", "Generate all metadata items", "Back..."]
        ret = xbmcgui.Dialog().select('Library Integration Tool - Staged Movies', lines)
        if not ret<0:
            if ret<len(staged_movies):   # staged item
                for i, item in enumerate(staged_movies):
                    if ret==i:
                        self.staged_movie_options(item)
            elif lines[ret]=='Add all movies':
                self.add_all_staged_movies()
            elif lines[ret]=='Add all movies with metadata':
                self.add_all_movies_with_metadata()
            elif lines[ret]=='Remove all items':
                self.remove_all_staged_movies()
            elif lines[ret]=='Generate all metadata items':
                self.generate_all_movie_metadata()
                return self.view_staged_movies()
            elif lines[ret]=='Back...':
                self.choose_action()
        else:
            self.choose_action()

    def add_all_staged_movies(self):
        pDialog = xbmcgui.DialogProgress()
        pDialog.create('Library Integration Tool', 'Adding all movies...')
        staged_items = get_items('staged.pkl')
        for item in staged_items:
            if item.get_mediatype()=='movie':
                pDialog.update(0,line2=item.get_title())
                item.add_to_library()
            else:
                pDialog.update(0,line2=' ')
        pDialog.close()
        xbmc.executebuiltin("Notification(\"Library Integration Tool\", \"All movies added\")")

    def add_all_movies_with_metadata(self):
        pDialog = xbmcgui.DialogProgress()
        pDialog.create('Library Integration Tool', 'Adding all movies with metadata...')
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
        xbmc.executebuiltin("Notification(\"Library Integration Tool\", \"All movies with metadata added\")")

    def remove_all_staged_movies(self):
        pDialog = xbmcgui.DialogProgress()
        pDialog.create('Library Integration Tool', 'Removing all movies...')
        staged_items = get_items('staged.pkl')
        for item in staged_items:
            if item.get_mediatype()=='movie':
                pDialog.update(0,line2=item.get_title())
                item.remove_from_staged()
            else:
                pDialog.update(0,line2=' ')
        pDialog.close()
        xbmc.executebuiltin("Notification(\"Library Integration Tool\", \"All movies removed\")")

    def generate_all_movie_metadata(self):
        pDialog = xbmcgui.DialogProgress()
        pDialog.create('Library Integration Tool', 'Generating all movie metadata...')
        staged_items = get_items('staged.pkl')
        for item in staged_items:
            if item.get_mediatype()=='movie':
                pDialog.update(0,line2=item.get_title())
                item.create_metadata_item()
            else:
                pDialog.update(0,line2=' ')
        pDialog.close()
        xbmc.executebuiltin("Notification(\"Library Integration Tool\", \"All movie metadata created\")")

    def staged_movie_options(self, item):
        lines = ["Add", "Remove", "Remove and block", "Rename", "Automatically rename using metadata", "Generate metadata item"]
        ret = xbmcgui.Dialog().select('Library Integration Tool - Staged Movie Options - %s' % item.get_title(), lines)
        if not ret<0:
            if lines[ret]=='Add':
                item.add_to_library()
            elif lines[ret]=='Remove':
                item.remove_from_staged()
            elif lines[ret]=='Remove and block':
                self.remove_and_block_movie(item)
            elif lines[ret]=='Rename':
                self.rename_staged_item(item)
                return self.staged_movie_options(item)
            elif lines[ret]=='Generate metadata item':
                item.create_metadata_item()
                return self.staged_movie_options(item)
            elif lines[ret]=='Automatically rename using metadata':
                item.rename_using_metadata()
                return self.staged_movie_options(item)
        self.view_staged_movies()

    def remove_and_block_movie(self, item):
        # add show title to blocked
        append_item('blocked.pkl', {'type':'movie', 'label':item.get_title()})
        # delete metadata items
        safe_title = clean(item.get_title())
        movie_dir = os.path.join(managed_folder, 'Metadata', 'Movies', safe_title)
        os.system('rm -r "%s"' % movie_dir)
        # remove from staged
        item.remove_from_staged()

    def view_staged_tvshows(self):
        staged_items = get_items('staged.pkl')
        staged_tvshows = [x.get_show_title() for x in staged_items if x.get_mediatype()=='tvshow']
        if len(staged_tvshows)==0:
            xbmcgui.Dialog().ok('Library Integration Tool', 'No staged TV shows')
            return self.choose_action()
        staged_tvshows = sorted(list(set(staged_tvshows)))
        lines = ['[B]%s[/B]' % x for x in staged_tvshows]
        lines += ["Add all TV shows", "Add all items with metadata", "Remove all TV shows", "Generate all metadata items", "Back..."]
        ret = xbmcgui.Dialog().select('Library Integration Tool - Staged TV Shows', lines)
        if not ret<0:
            if ret<len(staged_tvshows):   # staged item
                for show_title in staged_tvshows:
                    if staged_tvshows[ret]==show_title:
                        self.view_staged_tvshow_items(show_title)
            elif lines[ret]=='Add all TV shows':
                self.add_all_staged_tvshows()
            elif lines[ret]=='Add all items with metadata':
                self.add_all_tvshows_with_metadata()
                return self.view_staged_tvshows()
            elif lines[ret]=='Remove all TV Shows':
                self.remove_all_staged_tvshows()
            elif lines[ret]=='Generate all metadata items':
                self.generate_all_tvshow_metadata()
            elif lines[ret]=='Back...':
                self.choose_action()
        else:
            self.choose_action()

    def add_all_staged_tvshows(self):
        pDialog = xbmcgui.DialogProgress()
        pDialog.create('Library Integration Tool', 'Adding all TV shows...')
        staged_items = get_items('staged.pkl')
        for item in staged_items:
            if item.get_mediatype()=='tvshow':
                pDialog.update(0,line2=item.get_title())
                item.add_to_library()
            else:
                pDialog.update(0,line2=' ')
        pDialog.close()
        xbmc.executebuiltin("Notification(\"Library Integration Tool\", \"All TV shows added\")")

    def add_all_tvshows_with_metadata(self):
        pDialog = xbmcgui.DialogProgress()
        pDialog.create('Library Integration Tool', 'Adding all TV show items with metadata...')
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
        xbmc.executebuiltin("Notification(\"Library Integration Tool\", \"All TV show items with metadata added\")")

    def remove_all_staged_tvshows(self):
        pDialog = xbmcgui.DialogProgress()
        pDialog.create('Library Integration Tool', 'Removing all TV shows...')
        staged_items = get_items('staged.pkl')
        for item in staged_items:
            if item.get_mediatype()=='tvshow':
                pDialog.update(0,line2=item.get_title())
                item.remove_from_staged()
            else:
                pDialog.update(0,line2=' ')
        pDialog.close()
        xbmc.executebuiltin("Notification(\"Library Integration Tool\", \"All TV shows removed\")")

    def generate_all_tvshow_metadata(self):
        pDialog = xbmcgui.DialogProgress()
        pDialog.create('Library Integration Tool', 'Generating all TV show metadata...')
        staged_items = get_items('staged.pkl')
        for item in staged_items:
            if item.get_mediatype()=='tvshow':
                pDialog.update(0,line2=item.get_show_title(),line3=item.get_title())
                item.create_metadata_item()
            else:
                pDialog.update(0,line2=' ',line3=' ')
        pDialog.close()
        xbmc.executebuiltin("Notification(\"Library Integration Tool\", \"All TV show metadata created\")")

    def view_staged_tvshow_items(self, show_title):
        staged_items = get_items('staged.pkl')
        staged_episodes = [x for x in staged_items if x.get_mediatype()=='tvshow' and x.get_show_title()==show_title]
        if len(staged_episodes)==0:
            xbmcgui.Dialog().ok('Library Integration Tool', 'No staged %s episodes' % show_title)
            return self.view_staged_tvshows()
        lines = [str(x) for x in staged_episodes]
        lines, staged_episodes = (list(t) for t in zip(*sorted(zip(lines, staged_episodes))))
        lines += ["Add all episodes", "Add all episodes with metadata", "Remove all episodes", "Remove and block show", "Automatically rename all episodes using metadata", "Generate all metadata items", "Back..."]
        ret = xbmcgui.Dialog().select('Library Integration Tool - Staged %s Episodes' % show_title, lines)
        if not ret<0:
            if ret<len(staged_episodes):   # staged item
                for i, item in enumerate(staged_episodes):
                    if ret==i:
                        self.staged_episode_options(item)
            elif lines[ret]=='Add all episodes':
                self.add_all_staged_episodes(show_title)
                return self.view_staged_tvshows()
            elif lines[ret]=='Add all episodes with metadata':
                self.add_all_tvshow_items_with_metadata(show_title)
                return self.view_staged_tvshow_items(show_title)
            elif lines[ret]=='Remove all episodes':
                self.remove_all_staged_episodes(show_title)
                return self.view_staged_tvshows()
            elif lines[ret]=='Remove and block show':
                self.remove_and_block_staged_tvshow(show_title)
                return self.view_staged_tvshows()
            elif lines[ret]=='Automatically rename all episodes using metadata':
                self.rename_tvshow_using_metadata(show_title)
                return self.view_staged_tvshow_items(show_title)
            elif lines[ret]=='Generate all metadata items':
                self.generate_all_episodes_metadata(show_title)
                return self.view_staged_tvshow_items(show_title)
            elif lines[ret]=='Back...':
                self.view_staged_tvshows()
        else:
            self.view_staged_tvshows()

    def add_all_staged_episodes(self, show_title):
        pDialog = xbmcgui.DialogProgress()
        pDialog.create('Library Integration Tool', 'Adding all %s episodes...' % show_title)
        staged_items = get_items('staged.pkl')
        for item in staged_items:
            if item.get_mediatype()=='tvshow' and item.get_show_title()==show_title:
                pDialog.update(0,line2=item.get_title())
                item.add_to_library()
            else:
                pDialog.update(0,line2=' ')
        pDialog.close()
        xbmc.executebuiltin("Notification(\"Library Integration Tool\", \"All %s episodes added\")" % show_title)

    def add_all_tvshow_items_with_metadata(self, show_title):
        pDialog = xbmcgui.DialogProgress()
        pDialog.create('Library Integration Tool', 'Adding all %s episodes with metadata...' % show_title)
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
        xbmc.executebuiltin("Notification(\"Library Integration Tool\", \"All %s episodes with metadata added\")" % show_title)

    def remove_all_staged_episodes(self, show_title):
        pDialog = xbmcgui.DialogProgress()
        pDialog.create('Library Integration Tool', 'Removing all %s episodes...' % show_title)
        staged_items = get_items('staged.pkl')
        for item in staged_items:
            if item.get_mediatype()=='tvshow' and item.get_show_title()==show_title:
                pDialog.update(0,line2=item.get_title())
                item.remove_from_staged()
            else:
                pDialog.update(0,line2=' ')
        pDialog.close()
        xbmc.executebuiltin("Notification(\"Library Integration Tool\", \"All %s episodes removed\")" % show_title)

    def remove_and_block_staged_tvshow(self, show_title):
        # remove from staged
        self.remove_all_staged_episodes(show_title)
        # delete metadata folder
        safe_showtitle = clean(show_title)
        metadata_dir = os.path.join(managed_folder, 'Metadata', 'TV', safe_showtitle)
        os.system('rm -r "%s"' % metadata_dir)
        # add show title to blocked
        append_item('blocked.pkl', {'type':'show', 'label':show_title})

    def rename_tvshow_using_metadata(self, show_title):
        pDialog = xbmcgui.DialogProgress()
        pDialog.create('Library Integration Tool', 'Renaming all %s episodes using metadata...' % show_title)
        staged_items = get_items('staged.pkl')
        for item in staged_items:
            if item.get_mediatype()=='tvshow' and item.get_show_title()==show_title:
                pDialog.update(0,line2=item.get_title())
                item.rename_using_metadata()
            else:
                pDialog.update(0,line2=' ')
        pDialog.close()
        xbmc.executebuiltin("Notification(\"Library Integration Tool\", \"All %s episodes renamed using metadata\")" % show_title)

    def generate_all_episodes_metadata(self, show_title):
        pDialog = xbmcgui.DialogProgress()
        pDialog.create('Library Integration Tool', 'Generating all %s metadata...' % show_title)
        staged_items = get_items('staged.pkl')
        for item in staged_items:
            if item.get_mediatype()=='tvshow' and item.get_show_title()==show_title:
                pDialog.update(0,line2=item.get_title())
                item.create_metadata_item()
            else:
                pDialog.update(0,line2=' ')
        pDialog.close()
        xbmc.executebuiltin("Notification(\"Library Integration Tool\", \"All %s metadata created\")" % show_title)

    def staged_episode_options(self, item):
        #TODO: rename associated metadata when renaming
        #TODO: change item.show_title to item.get_show_title after I've rebuilt library
        #TODO: automatically rename based on nfo file for all items in tv show
        #TODO: rename show title
        #TODO: add to blocked movies/shows
        #TODO: remove item (including metadata)
        lines = ["Add", "Remove", "Remove and block episode", "Rename", "Automatically rename using metadata", "Generate metadata item", "Back..."]
        ret = xbmcgui.Dialog().select('Library Integration Tool - Staged Episode Options - %s' % item.get_title(), lines)
        if not ret<0:
            if lines[ret]=='Add':
                item.add_to_library()
                return self.view_staged_tvshow_items(item.get_show_title())
            elif lines[ret]=='Remove':
                item.remove_from_staged()
                return self.view_staged_tvshow_items(item.get_show_title())
            elif lines[ret]=='Remove and block episode':
                self.remove_and_block_episode(item)
                return self.view_staged_tvshow_items(item.get_show_title())
            elif lines[ret]=='Rename':
                self.rename_staged_item(item)
                return self.staged_episode_options(item)
            elif lines[ret]=='Generate metadata item':
                item.create_metadata_item()
                return self.staged_episode_options(item)
            elif lines[ret]=='Automatically rename using metadata':
                item.rename_using_metadata()
                return self.staged_episode_options(item)
            elif lines[ret]=='Back...':
                return self.view_staged_tvshow_items(item.get_show_title())
        else:
            self.view_staged_tvshow_items(item.get_show_title())

    def remove_and_block_episode(self, item):
        # add show title to blocked
        append_item('blocked.pkl', {'type':'episode', 'label':item.get_title()})
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
        #TODO: fix elif statements
        synced_dirs = get_items('synced.pkl')
        lines = ['%ss - [I]%s[/I]'%(x['mediatype'], x['dir']) for x in synced_dirs]
        lines += ["Update all", "Remove all", "Back..."]
        ret = xbmcgui.Dialog().select('Library Integration Tool - Synced Directories', lines)
        if not ret<0:
            if ret<len(synced_dirs):   # managed item
                for i, x in enumerate(synced_dirs):
                    if ret==i:
                        self.synced_dir_options(x)
            elif ret==len(synced_dirs):  #update all items
                self.update_all_synced(synced_dirs)
            elif ret==len(synced_dirs)+1:  #remove all items
                self.remove_all_synced()
            elif ret==len(synced_dirs)+2:  #back to previous view
                self.choose_action()
        else:
            self.choose_action()

    def synced_dir_options(self, item):
        #TODO: remove plugin
        lines = ["Update", "Remove"]
        ret = xbmcgui.Dialog().select('Library Integration Tool - Synced Directory Options - %s' % item['dir'], lines)
        if not ret<0:
            if lines[ret]=='Update':
                self.update_synced_dir(item)
            elif lines[ret]=='Remove':
                self.remove_synced_dir(item)
        self.view_synced()

    def remove_synced_dir(self, item):
        # TODO: remove staged and managed items added from this dir
        synced = get_items('synced.pkl')
        synced.remove(item)
        save_items('synced.pkl',synced)

    def remove_all_synced(self):
        if xbmcgui.Dialog().yesno("Library Integration Tool - Deleted all synced directories", 'Are you sure?'):
            save_items('synced.pkl', [])
            xbmc.executebuiltin("Notification(\"Library Integration Tool\", \"All synced directories removed\")")

    def update_synced_dir(self, item):
        # TODO: allow updating individual directories
        pass

    def update_all_synced(self, synced_dirs):
        #TODO: make it so manually added items don't just get deleted
        #TODO: don't initialize ContentItem until after confirmation
        #TODO: should move blocked check up to 'getting all items from ...'

        pDialog = xbmcgui.DialogProgress()
        pDialog.create('Library Integration Tool')

        # get current items in all directories
        pDialog.update(0, line1='Getting all items from synced directories...')
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
                    pDialog.update(0, line3=show_title)
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
        pDialog.update(0, line1='Finding items to remove from managed...')
        managed_items = get_items('managed.pkl')
        dir_paths = [x['file'] for x in dir_items]
        items_to_remove = []
        for item in managed_items:
            if item.get_path() not in dir_paths:
                pDialog.update(0, line2=item.get_title())
                items_to_remove.append(item)
            pDialog.update(0, line2=' ')


        # remove them from staged also (can do that immediately)
        pDialog.update(0, line1='Removing items from staged...')
        staged_items = get_items('staged.pkl')
        for item in staged_items:
            if item.get_path() not in dir_paths:
                pDialog.update(0, line2=item.get_title())
                item.remove_from_staged()
            pDialog.update(0, line2=' ')

        # find dir_items not in managed_items or staged_items, and prepare to add
        pDialog.update(0, line1='Finding items to add...')
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
            proceed = xbmcgui.Dialog().yesno("Library Integration Tool", '%i items to remove. %i items to stage.  Proceed?' % (num_to_remove,num_to_stage))
            if proceed:
                pDialog.update(0, line1='Removing items...')
                for item in items_to_remove:
                    log_msg('Removing from library: %s' % item.get_title(), xbmc.LOGNOTICE)
                    pDialog.update(0, line2=item.get_title())
                    item.remove_from_library()
                    pDialog.update(0, line2=' ')
                pDialog.update(0, line1='Staging items...')
                if num_to_stage>0:
                    staged_items += items_to_stage
                    save_items('staged.pkl',staged_items)
                    log_msg('Updated staged file with items from synced directories.', xbmc.LOGNOTICE)
                if num_to_remove>0:
                    xbmc.executebuiltin('CleanLibrary("video")')
                xbmc.executebuiltin("Notification(\"Library Integration Tool\", \"All synced directories updated\")")
        pDialog.close()

    def view_blocked(self):
        #TODO: sort
        #?TODO: change movie/episode to just path
        #?TODO: make blocked episode match on episode & show
        # types: show, movie, episode, keyword, plugin
        blocked_items = get_items('blocked.pkl')
        lines = ['[B]%s[/B] - %s' % (x['label'], x['type']) for x in blocked_items]
        lines += ["Add keyword", "Back..."]
        ret = xbmcgui.Dialog().select('Library Integration Tool - Blocked Items', lines)
        if not ret<0:
            if ret<len(blocked_items):   # managed item
                for i, x in enumerate(blocked_items):
                    if ret==i:
                        self.blocked_item_options(x)
            elif lines[ret]=='Add keyword':
                self.add_blocked_keyword()
                return self.view_blocked()
            elif lines[ret]=='Back...':
                self.choose_action()
        else:
            self.choose_action()

    def add_blocked_keyword(self):
        input_ret = xbmcgui.Dialog().input("Blocked keyword")
        if input_ret:
            append_item('blocked.pkl', {'type':'keyword', 'label':input_ret})

    def blocked_item_options(self, item):
        lines = ["Remove", "Back..."]
        ret = xbmcgui.Dialog().select('Library Integration Tool - Blocked item Options - %s' % item['label'], lines)
        if not ret<0:
            if lines[ret]=='Remove':
                remove_item('blocked.pkl', item)
                return self.view_blocked()
            elif lines[ret]=='Back...':
                self.view_blocked()
        self.view_blocked()
