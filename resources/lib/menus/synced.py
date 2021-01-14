#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Defines the SyncedMenu class
'''
# TODO: Different notifications depending on whether items were staged vs. automatically added

import sys

import xbmcgui
import xbmc
import resources.lib.utils as utils
from resources.lib.database_handler import DatabaseHandler

class SyncedMenu(object):
    ''' Provides windows for displaying synced directories,
    and tools for managing them and updating their contents '''

    # IDEA: new "find all directories" context item that finds and consolidates directories

    def __init__(self):
        self.dbh = DatabaseHandler()

    def filter_blocked_items(self, items, mediatype):
        ''' Filters out all blocked items in the list '''
        return [x for x in items if not self.dbh.check_blocked(x['label'], mediatype)]

    @utils.logged_function
    def find_items_to_stage(self, all_items):
        ''' Find items in the list not present in database '''
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

    @utils.logged_function
    def find_paths_to_remove(self, all_paths, **kwargs):
        ''' Find paths in database no longer available '''
        managed_items = self.dbh.get_content_items(**kwargs)
        return [x.path for x in managed_items if x.path not in all_paths]

    @utils.logged_function
    def get_movies_in_directory(self, directory):
        ''' Get all movies in the directory and tags them '''
        dir_items = self.filter_blocked_items(
            utils.load_directory_items(directory, recursive=True), 'movie'
        )

        for item in dir_items:
            # Add tag to items
            item['mediatype'] = 'movie'
        return dir_items

    @utils.logged_function
    def get_single_tvshow(self, directory, show_title):
        ''' Get the single TV show in the directory, and tag the items'''
        show_items = self.filter_blocked_items(
            utils.load_directory_items(directory, recursive=True), 'episode'
        )
        for item in show_items:
            # Add tag to items
            item['mediatype'] = 'tvshow'
            item['show_title'] = show_title
        return show_items

    @utils.logged_function
    def get_tvshows_in_directory(self, directory):
        ''' Get all TV shows in the directory, and tag the items '''
        dir_items = self.filter_blocked_items(
            utils.load_directory_items(directory, allow_directories=True, recursive=True), 'tvshow'
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

    def options(self, item):
        ''' Provide options for a single synced directory in a dialog window '''
        # TODO: Remove all from plugin
        # TODO: Rename label
        STR_REMOVE = utils.ADDON.getLocalizedString(32017)
        STR_SYNCED_DIR_OPTIONS = utils.ADDON.getLocalizedString(32085)
        STR_BACK = utils.ADDON.getLocalizedString(32011)
        lines = [STR_REMOVE, STR_BACK]
        ret = xbmcgui.Dialog().select(
            '{0} - {1} - {2}'.format(utils.ADDON_NAME, STR_SYNCED_DIR_OPTIONS, item['label']), lines
        )
        if ret >= 0:
            if lines[ret] == STR_REMOVE:
                self.dbh.remove_synced_dir(item['dir'])
            elif lines[ret] == STR_BACK:
                pass
        self.view()

    def remove_all(self):
        ''' Remove all synced directories '''
        STR_REMOVE_ALL_SYNCED_DIRS = utils.ADDON.getLocalizedString(32086)
        STR_ALL_SYNCED_DIRS_REMOVED = utils.ADDON.getLocalizedString(32087)
        STR_ARE_YOU_SURE = utils.ADDON.getLocalizedString(32088)
        if xbmcgui.Dialog().yesno('{0} - {1}'.format(utils.ADDON_NAME, STR_REMOVE_ALL_SYNCED_DIRS),
                                  STR_ARE_YOU_SURE):
            self.dbh.remove_all_synced_dirs()
            utils.notification(STR_ALL_SYNCED_DIRS_REMOVED)

    def remove_paths(self, paths_to_remove):
        ''' Remove and delete all items with the given paths '''
        for path in paths_to_remove:
            item = self.dbh.load_item(path)
            item.remove_from_library()
            item.delete()

    def stage_items(self, items_to_stage):
        ''' Stage all items in the list '''
        for item in items_to_stage:
            self.dbh.add_content_item(*item)

    @utils.logged_function
    def sync_movie_directory(self, dir_label, dir_path):
        ''' Sync movie directory and stage items '''
        STR_GETTING_ITEMS_IN_DIR = utils.ADDON.getLocalizedString(32125)
        STR_i_MOVIES_STAGED = utils.ADDON.getLocalizedString(32111)

        p_dialog = xbmcgui.DialogProgress()
        p_dialog.create(utils.ADDON_NAME)

        try:
            # Add synced directory to database
            self.dbh.add_synced_dir(dir_label, dir_path, 'movie')

            # Query json-rpc to get files in directory
            p_dialog.update(0, line1=STR_GETTING_ITEMS_IN_DIR)
            dir_items = utils.load_directory_items(dir_path, recursive=True)

            # Loop through all items and get titles and paths and stage them
            items_to_stage = 0
            for index, dir_item in enumerate(dir_items):
                # Get label & path for item
                item_label = dir_item['label']
                item_path = dir_item['file']
                if self.dbh.path_exists(item_path) or self.dbh.check_blocked(item_label, 'movie'):
                    continue
                # Update progress
                percent = 100 * index / len(dir_items)
                p_dialog.update(percent, line2=item_label)
                # Add item to database
                self.dbh.add_content_item(item_path, item_label, 'movie')
                items_to_stage += 1
                p_dialog.update(percent, line2=' ')
            utils.notification(STR_i_MOVIES_STAGED % items_to_stage)
        finally:
            p_dialog.close()

    @utils.logged_function
    def sync_single_movie(self, label, path):
        ''' Sync single movie path and stage item '''
        STR_ITEM_IS_ALREADY_STAGED = utils.ADDON.getLocalizedString(32103)
        STR_ITEM_IS_ALREADY_MANAGED = utils.ADDON.getLocalizedString(32104)
        STR_MOVIE_STAGED = utils.ADDON.getLocalizedString(32105)
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

    @utils.logged_function
    def sync_single_tvshow(self, show_label, show_path):
        ''' Sync single tvshow directory and stage items '''
        STR_i_NEW_i_STAGED_i_MANAGED = utils.ADDON.getLocalizedString(32106)
        STR_i_NEW = utils.ADDON.getLocalizedString(32107)
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

    # the names of epsodes will follow this model:
    # Euphoria (US) - S01E01 - Pilot.mkv
    # kodi/tinyMediaManager can detect this format without problems
    def new_epsode_name(self, showtitle, number, season=1, eptitle=None, full=None, half=None):
        # "eptitle": "Preaching Out Loud",
        # "number": 1,
        # "season": 1,
        # "showtitle": "Queer Eye",

        if number >= 100:
            epid = ('S0%sE%s' % (number, season))
        else:
            epid = ('S0%sE0%s' % (number, season))
            pass

        if full == True:
            return ('%s - %s - %s' % (showtitle, epid, eptitle))
        elif half == True:
            return ('%s - %s' % (epid, eptitle))
            pass

    @utils.logged_function
    def sync_tvshow_directory(self, dir_label, dir_path):
        ''' Sync all TV shows in directory and stage items'''
        STR_GETTING_ITEMS_IN_DIR = utils.ADDON.getLocalizedString(32125)
        STR_GETTING_ITEMS_IN_x = utils.ADDON.getLocalizedString(32126)
        STR_i_EPISODES_STAGED = utils.ADDON.getLocalizedString(32112)

        p_dialog = xbmcgui.DialogProgress()
        p_dialog.create(utils.ADDON_NAME)

        try:
            # add synced directory to database
            self.dbh.add_synced_dir(dir_label, dir_path, 'tvshow')

            # query json-rpc to get files in directory
            p_dialog.update(0, line1=STR_GETTING_ITEMS_IN_DIR)
            files_list = utils.load_directory_items(dir_path, allow_directories=True, recursive=True)

            items_to_stage = 0
            for index, showfile in enumerate(files_list):
                if 'showtitle' in showfile:
                    # Get name of show and skip if blocked
                    # Get everything inside tvshow path
                    filepath = showfile['file']
                    showtitle = showfile['showtitle']
                    try:
                        season = showfile['season']
                    except Exception as e:
                        season = 1
                    epnumber = showfile['number']
                    eptitle = showfile['eptitle']
                    newfilename = self.new_epsode_name(showtitle, season, epnumber, eptitle, full=True)
                    if self.dbh.check_blocked(showtitle, 'tvshow'):
                        continue
                    # Update progress
                    percent = 100 * index / len(files_list)
                    p_dialog.update(percent, line1=(STR_GETTING_ITEMS_IN_x % showtitle))
                    # Check for duplicate paths and blocked items
                    if self.dbh.path_exists(showfile['file']) or self.dbh.check_blocked(
                            showtitle, 'episode'):
                        continue
                    # Update progress
                    p_dialog.update(percent, line2=showtitle)
                    p_dialog.update(percent, line2=newfilename)
                    self.dbh.add_content_item(
                        showfile['file'], self.new_epsode_name(showtitle, season, epnumber, eptitle, half=True), 'tvshow', showtitle
                    )
                    items_to_stage += 1
                    # p_dialog.update(percent, line1=' ')
                    xbmc.sleep(150)
                    pass
            utils.notification(STR_i_EPISODES_STAGED % items_to_stage)
        finally:
            p_dialog.close()

    def update_all(self):
        ''' Get all items from synced directories, and
        find unavailable items to remove from managed,
        and new items to stage '''
        # TODO: bugfix: single-movies won't actually get removed if they become unavailable
        #       maybe load parent dir and check for path or label?  it would be slower though
        # TODO: option to only update specified or managed items
        # TODO: option to add update frequencies for specific directories (i.e. weekly/monthly/etc.)
        # TODO: better error handling when plugins dont load during update
        STR_FINDING_ITEMS_TO_REMOVE = utils.ADDON.getLocalizedString(32090)
        STR_FINDING_ITEMS_TO_ADD = utils.ADDON.getLocalizedString(32092)
        STR_i_TO_REMOVE_i_TO_STAGE_PROCEED = utils.ADDON.getLocalizedString(32093)
        STR_REMOVING_ITEMS = utils.ADDON.getLocalizedString(32094)
        STR_STAGING_ITEMS = utils.ADDON.getLocalizedString(32095)
        STR_ALL_ITEMS_UPTODATE = utils.ADDON.getLocalizedString(32121)
        STR_SUCCESS = utils.ADDON.getLocalizedString(32122)

        p_dialog = xbmcgui.DialogProgressBG()
        p_dialog.create(utils.ADDON_NAME)

        try:
            # Get current items in all directories
            synced_dirs = self.dbh.get_synced_dirs()
            all_items = []
            for index, synced_dir in enumerate(synced_dirs):
                p_dialog.update(
                    percent=99 * index / len(synced_dirs),
                    message='{label} - {type}'.format(
                        label=synced_dir['label'], type=synced_dir.localize_type()
                    )
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
                if xbmcgui.Dialog().yesno(utils.ADDON_NAME, STR_i_TO_REMOVE_i_TO_STAGE_PROCEED %
                                          (len(paths_to_remove), len(items_to_stage))):
                    if paths_to_remove:
                        p_dialog.update(percent=99, message=STR_REMOVING_ITEMS)
                        self.remove_paths(paths_to_remove)
                    if items_to_stage:
                        p_dialog.update(percent=99, message=STR_STAGING_ITEMS)
                        self.stage_items(items_to_stage)
                    # TODO: update/clean managed folder
                    xbmcgui.Dialog().ok(utils.ADDON_NAME, STR_SUCCESS)
            else:
                xbmcgui.Dialog().ok(utils.ADDON_NAME, STR_ALL_ITEMS_UPTODATE)
        finally:
            p_dialog.close()

    def update_movies(self):
        ''' Update all synced movie directories '''
        STR_FINDING_ITEMS_TO_REMOVE = utils.ADDON.getLocalizedString(32090)
        STR_FINDING_ITEMS_TO_ADD = utils.ADDON.getLocalizedString(32092)
        STR_i_TO_REMOVE_i_TO_STAGE_PROCEED = utils.ADDON.getLocalizedString(32093)
        STR_REMOVING_ITEMS = utils.ADDON.getLocalizedString(32094)
        STR_STAGING_ITEMS = utils.ADDON.getLocalizedString(32095)
        STR_ALL_ITEMS_UPTODATE = utils.ADDON.getLocalizedString(32121)
        STR_SUCCESS = utils.ADDON.getLocalizedString(32122)

        p_dialog = xbmcgui.DialogProgressBG()
        p_dialog.create(utils.ADDON_NAME)

        try:
            all_items = []
            movie_dirs = self.dbh.get_synced_dirs(synced_type='movie')
            single_movie_dirs = self.dbh.get_synced_dirs(synced_type='single-movie')
            total_num_dirs = len(movie_dirs + single_movie_dirs)

            for index, synced_dir in enumerate(movie_dirs):
                p_dialog.update(percent=99 * index / total_num_dirs, message=synced_dir['label'])
                all_items += self.get_movies_in_directory(synced_dir['dir'])

            for index, synced_dir in enumerate(single_movie_dirs):
                p_dialog.update(
                    percent=99 * (index + len(movie_dirs)) / total_num_dirs,
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
                if xbmcgui.Dialog().yesno(utils.ADDON_NAME, STR_i_TO_REMOVE_i_TO_STAGE_PROCEED %
                                          (len(paths_to_remove), len(items_to_stage))):
                    if paths_to_remove:
                        p_dialog.update(percent=99, message=STR_REMOVING_ITEMS)
                        self.remove_paths(paths_to_remove)
                    if items_to_stage:
                        p_dialog.update(percent=99, message=STR_STAGING_ITEMS)
                        self.stage_items(items_to_stage)
                    # TODO: update/clean managed folder
                    xbmcgui.Dialog().ok(utils.ADDON_NAME, STR_SUCCESS)
            else:
                xbmcgui.Dialog().ok(utils.ADDON_NAME, STR_ALL_ITEMS_UPTODATE)
        finally:
            p_dialog.close()

    def update_tvshows(self):
        ''' Update all TV show directories '''
        STR_FINDING_ITEMS_TO_REMOVE = utils.ADDON.getLocalizedString(32090)
        STR_FINDING_ITEMS_TO_ADD = utils.ADDON.getLocalizedString(32092)
        STR_i_TO_REMOVE_i_TO_STAGE_PROCEED = utils.ADDON.getLocalizedString(32093)
        STR_REMOVING_ITEMS = utils.ADDON.getLocalizedString(32094)
        STR_STAGING_ITEMS = utils.ADDON.getLocalizedString(32095)
        STR_ALL_ITEMS_UPTODATE = utils.ADDON.getLocalizedString(32121)
        STR_SUCCESS = utils.ADDON.getLocalizedString(32122)

        p_dialog = xbmcgui.DialogProgressBG()
        p_dialog.create(utils.ADDON_NAME)

        try:
            all_items = []
            show_dirs = self.dbh.get_synced_dirs(synced_type='tvshow')
            single_show_dirs = self.dbh.get_synced_dirs(synced_type='single-tvshow')
            total_num_dirs = len(show_dirs + single_show_dirs)

            for index, synced_dir in enumerate(show_dirs):
                p_dialog.update(percent=99 * index / total_num_dirs, message=synced_dir['label'])
                all_items += self.get_tvshows_in_directory(synced_dir['dir'])

            for index, synced_dir in enumerate(single_show_dirs):
                p_dialog.update(
                    percent=99. * (index + len(show_dirs)) / total_num_dirs,
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
                if xbmcgui.Dialog().yesno(utils.ADDON_NAME, STR_i_TO_REMOVE_i_TO_STAGE_PROCEED %
                                          (len(paths_to_remove), len(items_to_stage))):
                    if paths_to_remove:
                        p_dialog.update(percent=99, message=STR_REMOVING_ITEMS)
                        self.remove_paths(paths_to_remove)
                    if items_to_stage:
                        p_dialog.update(percent=99, message=STR_STAGING_ITEMS)
                        self.stage_items(items_to_stage)
                    # TODO: update/clean managed folder
                    xbmcgui.Dialog().ok(utils.ADDON_NAME, STR_SUCCESS)
            else:
                xbmcgui.Dialog().ok(utils.ADDON_NAME, STR_ALL_ITEMS_UPTODATE)
        finally:
            p_dialog.close()

    @utils.logged_function
    def view(self):
        ''' Display all synced directories, which are selectable and lead to options.
        Also provides additional options at bottom of menu '''
        STR_UPDATE_ALL = utils.ADDON.getLocalizedString(32081)
        STR_UPDATE_TV_SHOWS = utils.ADDON.getLocalizedString(32137)
        STR_UPDATE_MOVIES = utils.ADDON.getLocalizedString(32138)
        STR_REMOVE_ALL = utils.ADDON.getLocalizedString(32082)
        STR_BACK = utils.ADDON.getLocalizedString(32011)
        STR_SYNCED_DIRECTORIES = utils.ADDON.getLocalizedString(32128)
        STR_NO_SYNCED_DIRS = utils.ADDON.getLocalizedString(32120)
        synced_dirs = self.dbh.get_synced_dirs()
        if not synced_dirs:
            xbmcgui.Dialog().ok(utils.ADDON_NAME, STR_NO_SYNCED_DIRS)
            return
        lines = [
            '[B]%s[/B] - %s - [I]%s[/I]' % (x['label'].decode('utf-8'), x.localize_type(), x['dir'])
            for x in synced_dirs
        ]
        lines += [STR_UPDATE_ALL, STR_UPDATE_MOVIES, STR_UPDATE_TV_SHOWS, STR_REMOVE_ALL, STR_BACK]
        ret = xbmcgui.Dialog().select(
            '{0} - {1}'.format(utils.ADDON_NAME, STR_SYNCED_DIRECTORIES), lines
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
