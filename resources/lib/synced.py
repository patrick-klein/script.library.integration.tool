#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
This module contains the class Synced,
which provide dialog windows and tools for manged synced directories
'''

import sys

import xbmc
import xbmcgui
import xbmcaddon

import database_handler as db
import resources.lib.utils as utils


class SyncedItem(dict):
    '''  '''

    def __init__(self, directory, label, synced_type):
        super(SyncedItem, self).__init__()
        self['dir'] = directory
        self['label'] = label
        self['type'] = synced_type


class Synced(object):
    '''
    Provides windows for displaying synced directories,
    and tools for managing them and updating their contents
    '''

    #IDEA: new "find all directories" context item that finds and consolidates directories

    def __init__(self):
        self.addon = xbmcaddon.Addon()
        self.STR_ADDON_NAME = self.addon.getAddonInfo('name')
        self.dbh = db.DatabaseHandler()

    def filter_blocked_items(self, items, mediatype):
        '''  '''
        return [x for x in items if not self.dbh.check_blocked(x['label'], mediatype)]

    @utils.log_decorator
    def find_items_to_stage(self, all_items):
        '''  '''
        items_to_stage = []
        for dir_item in all_items:
            path = dir_item['file']
            # Don't prepare items that are already staged or managed
            if self.dbh.path_exists(path):
                continue
            label = dir_item['label']
            mediatype = dir_item['mediatype']
            if mediatype == 'movie':
                item = (path, label, mediatype)
            elif mediatype == 'tvshow':
                item = (path, label, mediatype, dir_item['show_title'])
            items_to_stage.append(item)
        return items_to_stage

    @utils.log_decorator
    def find_paths_to_remove(self, all_paths, **kwargs):
        '''  '''
        managed_items = self.dbh.get_content_items(**kwargs)
        return [x.get_path() for x in managed_items if x.get_path() not in all_paths]

    @utils.log_decorator
    def get_movies_in_directory(self, directory):
        '''  '''
        dir_items = self.filter_blocked_items(
            utils.load_directory_items(directory, recursive=True), 'movie'
        )
        for item in dir_items:
            # Add tag to items
            item['mediatype'] = 'movie'
        return dir_items

    @utils.log_decorator
    def get_single_tvshow(self, directory, show_title):
        ''' '''
        show_items = self.filter_blocked_items(
            utils.load_directory_items(directory, recursive=True), 'episode'
        )
        for item in show_items:
            # Add tag to items
            item['mediatype'] = 'tvshow'
            item['show_title'] = show_title
        return show_items

    @utils.log_decorator
    def get_tvshows_in_directory(self, directory):
        '''  '''
        dir_items = self.filter_blocked_items(
            utils.load_directory_items(directory, allow_directories=True), 'tvshow'
        )
        all_items = []
        # Check every tvshow in list
        for dir_item in dir_items:
            show_title = dir_item['label']
            # Load results if show isn't blocked
            show_path = dir_item['file']
            show_items = self.filter_blocked_items(
                utils.load_directory_items(show_path, recursive=True), 'episode'
            )
            for show_item in show_items:
                # Add formatted item
                show_item['mediatype'] = 'tvshow'
                show_item['show_title'] = show_title
            all_items += show_items
        return all_items

    def localize_type(self, mediatype):
        ''' Localizes tags used for identifying mediatype '''
        if mediatype == 'movie':  # Movies
            return self.addon.getLocalizedString(32109)
        elif mediatype == 'tvshow':  # TV Shows
            return self.addon.getLocalizedString(32108)
        elif mediatype == 'single-movie':  # Single Movie
            return self.addon.getLocalizedString(32116)
        elif mediatype == 'single-tvshow':  # Single TV Show
            return self.addon.getLocalizedString(32115)
        return mediatype

    def options(self, item):
        ''' Provides options for a single synced directory in a dialog window '''
        #TODO: remove all from plugin
        #TODO: rename label
        STR_REMOVE = self.addon.getLocalizedString(32017)
        STR_SYNCED_DIR_OPTIONS = self.addon.getLocalizedString(32085)
        STR_BACK = self.addon.getLocalizedString(32011)
        lines = [STR_REMOVE, STR_BACK]
        ret = xbmcgui.Dialog().select(
            '{0} - {1} - {2}'.format(self.STR_ADDON_NAME, STR_SYNCED_DIR_OPTIONS, item['label']),
            lines
        )
        if ret >= 0:
            if lines[ret] == STR_REMOVE:
                self.dbh.remove_synced_dir(item['dir'])
            elif lines[ret] == STR_BACK:
                pass
        self.view()

    def remove_all(self):
        ''' Removes all synced directories '''
        STR_REMOVE_ALL_SYNCED_DIRS = self.addon.getLocalizedString(32086)
        STR_ALL_SYNCED_DIRS_REMOVED = self.addon.getLocalizedString(32087)
        STR_ARE_YOU_SURE = self.addon.getLocalizedString(32088)
        if xbmcgui.Dialog().yesno('{0} - {1}'.format(self.STR_ADDON_NAME,
                                                     STR_REMOVE_ALL_SYNCED_DIRS), STR_ARE_YOU_SURE):
            self.dbh.remove_all_synced_dirs()
            utils.notification(STR_ALL_SYNCED_DIRS_REMOVED)

    def remove_paths(self, paths_to_remove):
        '''  '''
        for path in paths_to_remove:
            item = self.dbh.load_item(path)
            item.remove_from_library()
            item.delete()

    def stage_items(self, items_to_stage):
        '''  '''
        for item in items_to_stage:
            self.dbh.add_content_item(*item)

    @utils.log_decorator
    def sync_movie_directory(self, dir_label, dir_path):
        ''' '''
        STR_GETTING_ITEMS_IN_DIR = self.addon.getLocalizedString(32125)
        STR_i_MOVIES_STAGED = self.addon.getLocalizedString(32111)

        p_dialog = xbmcgui.DialogProgress()
        p_dialog.create(self.STR_ADDON_NAME)

        try:
            # add synced directory to database
            self.dbh.add_synced_dir(dir_label, dir_path, 'movie')

            # query json-rpc to get files in directory
            p_dialog.update(0, line1=STR_GETTING_ITEMS_IN_DIR)
            dir_items = utils.load_directory_items(dir_path, recursive=True)

            # loop through all items and get titles and paths and stage them
            items_to_stage = 0
            for dir_item in dir_items:
                # get label & path for item
                item_label = dir_item['label']
                item_path = dir_item['file']
                if self.dbh.path_exists(item_path) or self.dbh.check_blocked(item_label, 'movie'):
                    continue
                # update progress
                p_dialog.update(0, line2=item_label)
                # add item to database
                self.dbh.add_content_item(item_path, item_label, 'movie')
                items_to_stage += 1
                p_dialog.update(0, line2=' ')
            utils.notification(STR_i_MOVIES_STAGED % items_to_stage)
        finally:
            p_dialog.close()

    @utils.log_decorator
    def sync_single_movie(self, label, path):
        ''' '''
        STR_ITEM_IS_ALREADY_STAGED = self.addon.getLocalizedString(32103)
        STR_ITEM_IS_ALREADY_MANAGED = self.addon.getLocalizedString(32104)
        STR_MOVIE_STAGED = self.addon.getLocalizedString(32105)
        # Add synced directory to database
        self.dbh.add_synced_dir(label, path, 'single-movie')
        # Check for duplicate in database
        if self.dbh.path_exists(path, 'staged'):
            utils.notification(STR_ITEM_IS_ALREADY_STAGED)
        elif self.dbh.path_exists(path, 'managed'):
            utils.notification(STR_ITEM_IS_ALREADY_MANAGED)
        else:
            # Add item to database
            self.dbh.add_content_item(path, label, 'movie')
            utils.notification(STR_MOVIE_STAGED)

    @utils.log_decorator
    def sync_single_tvshow(self, show_label, show_path):
        ''' '''
        STR_i_NEW_i_STAGED_i_MANAGED = self.addon.getLocalizedString(32106)
        STR_i_NEW = self.addon.getLocalizedString(32107)
        # Add synced directory to database
        self.dbh.add_synced_dir(show_label, show_path, 'single-tvshow')
        # Get everything inside tvshow path
        dir_items = utils.load_directory_items(show_path, recursive=True)
        # Get all items to stage
        items_to_stage = 0
        num_already_staged = 0
        num_already_managed = 0
        for dir_item in dir_items:
            item_label = dir_item['label']
            item_path = dir_item['file']
            if self.dbh.path_exists(item_path, 'staged'):
                num_already_staged += 1
                continue
            elif self.dbh.path_exists(item_path, 'managed'):
                num_already_managed += 1
                continue
            elif self.dbh.check_blocked(item_label, 'episode'):
                continue
            self.dbh.add_content_item(item_path, item_label, 'tvshow', show_label)
            items_to_stage += 1
        if num_already_staged > 0 or num_already_managed > 0:
            utils.notification(
                STR_i_NEW_i_STAGED_i_MANAGED %
                (items_to_stage, num_already_staged, num_already_managed)
            )
        else:
            utils.notification(STR_i_NEW % items_to_stage)

    @utils.log_decorator
    def sync_tvshow_directory(self, dir_label, dir_path):
        ''' '''
        STR_GETTING_ITEMS_IN_DIR = self.addon.getLocalizedString(32125)
        STR_GETTING_ITEMS_IN_x = self.addon.getLocalizedString(32126)
        STR_i_EPISODES_STAGED = self.addon.getLocalizedString(32112)

        p_dialog = xbmcgui.DialogProgress()
        p_dialog.create(self.STR_ADDON_NAME)

        try:
            # add synced directory to database
            self.dbh.add_synced_dir(dir_label, dir_path, 'tvshow')

            # query json-rpc to get files in directory
            p_dialog.update(0, line1=STR_GETTING_ITEMS_IN_DIR)
            dir_items = utils.load_directory_items(dir_path, allow_directories=True)

            items_to_stage = 0
            for index, dir_item in enumerate(dir_items):
                # Get name of show and skip if blocked
                tvshow_label = dir_item['label']
                if self.dbh.check_blocked(tvshow_label, 'tvshow'):
                    continue
                # Update progress
                p_dialog.update(
                    int(100. * index / len(dir_items)),
                    line1=(STR_GETTING_ITEMS_IN_x % tvshow_label)
                )
                # Get everything inside tvshow path
                tvshow_path = dir_item['file']
                show_items = utils.load_directory_items(tvshow_path, recursive=True)
                # Get all items to stage in show
                for show_item in show_items:
                    # Check for duplicate paths and blocked items
                    if self.dbh.path_exists(show_item['file']) or self.dbh.check_blocked(
                            show_item['label'], 'episode'):
                        continue
                    # Update progress
                    p_dialog.update(0, line2=show_item['label'])
                    self.dbh.add_content_item(
                        show_item['file'], show_item['label'], 'tvshow', tvshow_label
                    )
                    items_to_stage += 1
                    p_dialog.update(0, line2=' ')
                p_dialog.update(0, line1=' ')
            utils.notification(STR_i_EPISODES_STAGED % items_to_stage)
        finally:
            p_dialog.close()

    def update_all(self):
        '''
        Gets all items from synced directories,
        then finds unavailable items to remove from managed,
        and new items to stage
        '''
        #TODO: wait until after confirmation to remove staged items also
        #TODO: bugfix: single-movies won't actually get removed if they become unavailable
        #       maybe load parent dir and check for path or label?  it would be slower though
        #TODO: option to only update specified or managed items
        #TODO: option to add update frequencies for specific directories (i.e. weekly/monthly/etc.)
        #TODO: better error handling when plugins dont load during update (make it similar to clean)
        #TODO: show synced label in progress bar if available instead of path
        STR_FINDING_ITEMS_TO_REMOVE = self.addon.getLocalizedString(32090)
        STR_FINDING_ITEMS_TO_ADD = self.addon.getLocalizedString(32092)
        STR_i_TO_REMOVE_i_TO_STAGE_PROCEED = self.addon.getLocalizedString(32093)
        STR_REMOVING_ITEMS = self.addon.getLocalizedString(32094)
        STR_STAGING_ITEMS = self.addon.getLocalizedString(32095)
        STR_ALL_ITEMS_UPTODATE = self.addon.getLocalizedString(32121)
        STR_SUCCESS = self.addon.getLocalizedString(32122)

        p_dialog = xbmcgui.DialogProgressBG()
        p_dialog.create(self.STR_ADDON_NAME)

        try:
            # Get current items in all directories
            synced_dirs = self.dbh.get_synced_dirs()
            all_items = []
            for index, synced_dir in enumerate(synced_dirs):
                p_dialog.update(
                    percent=int(99. * index / len(synced_dirs)), message=synced_dir['label']
                )
                if synced_dir['type'] == 'single-movie':
                    # Directory is just a path to a single movie
                    all_items.append({
                        'file': synced_dir['dir'],
                        'label': synced_dir['label'],
                        'mediatype': 'movie'
                    })
                elif synced_dir['type'] == 'single-tvshow':
                    # Directory is a path to a tv show folder
                    all_items += self.get_single_tvshow(synced_dir['dir'], synced_dir['label'])
                elif synced_dir['type'] == 'movie':
                    # Directory is a path to list of movies
                    all_items += self.get_movies_in_directory(synced_dir['dir'])
                elif synced_dir['type'] == 'tvshow':
                    # Directory is a path to a list of tv shows
                    all_items += self.get_tvshows_in_directory(synced_dir['dir'])

            # Find managed paths not in dir_items, and prepare to remove
            p_dialog.update(percent=99, message=STR_FINDING_ITEMS_TO_REMOVE)
            all_paths = [x['file'] for x in all_items]
            paths_to_remove = self.find_paths_to_remove(all_paths)

            # Find dir_items not in managed_items or staged_items, and prepare to add
            p_dialog.update(percent=99, message=STR_FINDING_ITEMS_TO_ADD)
            items_to_stage = self.find_items_to_stage(all_items)

            # Prompt user to remove & stage
            if paths_to_remove or items_to_stage:
                if xbmcgui.Dialog().yesno(self.STR_ADDON_NAME, STR_i_TO_REMOVE_i_TO_STAGE_PROCEED %
                                          (len(paths_to_remove), len(items_to_stage))):
                    if paths_to_remove:
                        p_dialog.update(percent=99, message=STR_REMOVING_ITEMS)
                        self.remove_paths(paths_to_remove)
                    if items_to_stage:
                        p_dialog.update(percent=99, message=STR_STAGING_ITEMS)
                        self.stage_items(items_to_stage)
                    xbmcgui.Dialog().ok(self.STR_ADDON_NAME, STR_SUCCESS)
            else:
                xbmcgui.Dialog().ok(self.STR_ADDON_NAME, STR_ALL_ITEMS_UPTODATE)
        finally:
            p_dialog.close()

    def update_movies(self):
        '''  '''
        STR_FINDING_ITEMS_TO_REMOVE = self.addon.getLocalizedString(32090)
        STR_FINDING_ITEMS_TO_ADD = self.addon.getLocalizedString(32092)
        STR_i_TO_REMOVE_i_TO_STAGE_PROCEED = self.addon.getLocalizedString(32093)
        STR_REMOVING_ITEMS = self.addon.getLocalizedString(32094)
        STR_STAGING_ITEMS = self.addon.getLocalizedString(32095)
        STR_ALL_ITEMS_UPTODATE = self.addon.getLocalizedString(32121)
        STR_SUCCESS = self.addon.getLocalizedString(32122)

        p_dialog = xbmcgui.DialogProgressBG()
        p_dialog.create(self.STR_ADDON_NAME)

        try:
            all_items = []
            movie_dirs = self.dbh.get_synced_dirs(synced_type='movie')
            single_movie_dirs = self.dbh.get_synced_dirs(synced_type='single-movie')
            total_num_dirs = len(movie_dirs + single_movie_dirs)

            for index, synced_dir in enumerate(movie_dirs):
                p_dialog.update(
                    percent=int(99. * index / total_num_dirs), message=synced_dir['label']
                )
                all_items += self.get_movies_in_directory(synced_dir['dir'])

            for index, synced_dir in enumerate(single_movie_dirs):
                p_dialog.update(
                    percent=int(99. * (index + len(movie_dirs)) / total_num_dirs),
                    message=synced_dir['label']
                )
                all_items.append({
                    'file': synced_dir['dir'],
                    'label': synced_dir['label'],
                    'mediatype': 'movie'
                })

            # Find managed paths not in dir_items, and prepare to remove
            p_dialog.update(percent=99, message=STR_FINDING_ITEMS_TO_REMOVE)
            all_paths = [x['file'] for x in all_items]
            paths_to_remove = self.find_paths_to_remove(all_paths, mediatype='movie')

            # Find dir_items not in managed_items or staged_items, and prepare to add
            p_dialog.update(percent=99, message=STR_FINDING_ITEMS_TO_ADD)
            items_to_stage = self.find_items_to_stage(all_items)

            # Prompt user to remove & stage
            if paths_to_remove or items_to_stage:
                if xbmcgui.Dialog().yesno(self.STR_ADDON_NAME, STR_i_TO_REMOVE_i_TO_STAGE_PROCEED %
                                          (len(paths_to_remove), len(items_to_stage))):
                    if paths_to_remove:
                        p_dialog.update(percent=99, message=STR_REMOVING_ITEMS)
                        self.remove_paths(paths_to_remove)
                    if items_to_stage:
                        p_dialog.update(percent=99, message=STR_STAGING_ITEMS)
                        self.stage_items(items_to_stage)
                    xbmcgui.Dialog().ok(self.STR_ADDON_NAME, STR_SUCCESS)
            else:
                xbmcgui.Dialog().ok(self.STR_ADDON_NAME, STR_ALL_ITEMS_UPTODATE)
        finally:
            p_dialog.close()

    def update_tvshows(self):
        '''  '''
        STR_FINDING_ITEMS_TO_REMOVE = self.addon.getLocalizedString(32090)
        STR_FINDING_ITEMS_TO_ADD = self.addon.getLocalizedString(32092)
        STR_i_TO_REMOVE_i_TO_STAGE_PROCEED = self.addon.getLocalizedString(32093)
        STR_REMOVING_ITEMS = self.addon.getLocalizedString(32094)
        STR_STAGING_ITEMS = self.addon.getLocalizedString(32095)
        STR_ALL_ITEMS_UPTODATE = self.addon.getLocalizedString(32121)
        STR_SUCCESS = self.addon.getLocalizedString(32122)

        p_dialog = xbmcgui.DialogProgressBG()
        p_dialog.create(self.STR_ADDON_NAME)

        try:
            all_items = []
            show_dirs = self.dbh.get_synced_dirs(synced_type='tvshow')
            single_show_dirs = self.dbh.get_synced_dirs(synced_type='single-tvshow')
            total_num_dirs = len(show_dirs + single_show_dirs)

            for index, synced_dir in enumerate(show_dirs):
                p_dialog.update(
                    percent=int(99. * index / total_num_dirs), message=synced_dir['label']
                )
                all_items += self.get_tvshows_in_directory(synced_dir['dir'])

            for index, synced_dir in enumerate(single_show_dirs):
                p_dialog.update(
                    percent=int(99. * (index + len(show_dirs)) / total_num_dirs),
                    message=synced_dir['label']
                )
                all_items += self.get_single_tvshow(synced_dir['dir'], synced_dir['label'])

            # Find managed paths not in dir_items, and prepare to remove
            p_dialog.update(percent=99, message=STR_FINDING_ITEMS_TO_REMOVE)
            all_paths = [x['file'] for x in all_items]
            paths_to_remove = self.find_paths_to_remove(all_paths, mediatype='tvshow')

            # Find dir_items not in managed_items or staged_items, and prepare to add
            p_dialog.update(percent=99, message=STR_FINDING_ITEMS_TO_ADD)
            items_to_stage = self.find_items_to_stage(all_items)

            # Prompt user to remove & stage
            if paths_to_remove or items_to_stage:
                if xbmcgui.Dialog().yesno(self.STR_ADDON_NAME, STR_i_TO_REMOVE_i_TO_STAGE_PROCEED %
                                          (len(paths_to_remove), len(items_to_stage))):
                    if paths_to_remove:
                        p_dialog.update(percent=99, message=STR_REMOVING_ITEMS)
                        self.remove_paths(paths_to_remove)
                    if items_to_stage:
                        p_dialog.update(percent=99, message=STR_STAGING_ITEMS)
                        self.stage_items(items_to_stage)
                    xbmcgui.Dialog().ok(self.STR_ADDON_NAME, STR_SUCCESS)
            else:
                xbmcgui.Dialog().ok(self.STR_ADDON_NAME, STR_ALL_ITEMS_UPTODATE)
        finally:
            p_dialog.close()

    @utils.log_decorator
    def view(self):
        '''
        Displays all synced directories, which are selectable and lead to options.
        Also provides additional options at bottom of menu.
        '''
        #TODO: update only movies or tvshows
        STR_UPDATE_ALL = self.addon.getLocalizedString(32081)
        STR_UPDATE_TV_SHOWS = self.addon.getLocalizedString(32137)
        STR_UPDATE_MOVIES = self.addon.getLocalizedString(32138)
        STR_REMOVE_ALL = self.addon.getLocalizedString(32082)
        STR_BACK = self.addon.getLocalizedString(32011)
        STR_SYNCED_DIRECTORIES = self.addon.getLocalizedString(32128)
        STR_NO_SYNCED_DIRS = self.addon.getLocalizedString(32120)
        synced_dirs = self.dbh.get_synced_dirs()
        if not synced_dirs:
            xbmcgui.Dialog().ok(self.STR_ADDON_NAME, STR_NO_SYNCED_DIRS)
            return
        lines = [
            '[B]%s[/B] - %s - [I]%s[/I]' % (x['label'], self.localize_type(x['type']), x['dir'])
            for x in synced_dirs
        ]
        lines += [STR_UPDATE_ALL, STR_UPDATE_MOVIES, STR_UPDATE_TV_SHOWS, STR_REMOVE_ALL, STR_BACK]
        ret = xbmcgui.Dialog().select(
            '{0} - {1}'.format(self.STR_ADDON_NAME, STR_SYNCED_DIRECTORIES), lines
        )
        if ret >= 0:
            if ret < len(synced_dirs):
                for index, directory in enumerate(synced_dirs):
                    if ret == index:
                        self.options(directory)
                        break
            elif lines[ret] == STR_UPDATE_ALL:
                self.update_all()
                sys.exit()
            elif lines[ret] == STR_UPDATE_MOVIES:
                self.update_movies()
                sys.exit()
            elif lines[ret] == STR_UPDATE_TV_SHOWS:
                self.update_tvshows()
                sys.exit()
            elif lines[ret] == STR_REMOVE_ALL:
                self.remove_all()
            elif lines[ret] == STR_BACK:
                return
