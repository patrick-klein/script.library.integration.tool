#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Defines the SyncedMenu class."""

# TODO: Different notifications depending on whether items were staged vs. automatically added
import sys

import xbmc # pylint: disable=import-error
import xbmcgui # pylint: disable=import-error

from resources import ADDON_NAME

from resources.lib import build_json_item
from resources.lib import build_contentitem

from resources.lib.log import logged_function

from resources.lib.utils import notification
from resources.lib.utils import title_with_color
from resources.lib.utils import getlocalizedstring
from resources.lib.utils import load_directory_items


class SyncedMenu(object):
    """Provides windows for displaying synced directories,
    and tools for managing them and updating their contents."""

    # IDEA: new "find all directories" context item that finds and consolidates directories

    def __init__(self, database):
        """SyncedMenu class."""
        self.database = database
        self.progressdialog = xbmcgui.DialogProgress()


    def filter_blocked_items(self, items, _type):
        """Filters out all blocked items in the list."""
        return [x for x in items if not self.database.check_blocked(x['label'], _type)]


    @logged_function
    def find_items_to_stage(self, all_items):
        """Find items in the list not present in database."""
        items_to_stage = []
        for jsonitem in all_items:
            file = jsonitem['file']
            label = jsonitem['label']
            _type = jsonitem['type']
            if self.database.path_exists(file=file):
                continue
            if _type == 'movie':
                items_to_stage.append((file, label, _type))
            elif _type in ['tvshow', 'episode']:
                items_to_stage.append((file, label, _type, jsonitem['showtitle']))
        return items_to_stage


    @logged_function
    def find_paths_to_remove(self, all_paths, **kwargs):
        """Find paths in database no longer available."""
        #TODO: update this func in future
        managed_items = self.database.get_content_items(**kwargs)
        return [x.path for x in managed_items if x.path not in all_paths]


    @logged_function
    def get_movies_in_directory(self, directory):
        """Get all movies in the directory and tags them."""
        dir_items = self.filter_blocked_items(
            list(load_directory_items(
                progressdialog=None,
                _path=directory,
                recursive=True,
                sync_type='movie'
                )), _type='movie'
            )
        # TODO: this loop aparently not realy work
        for item in dir_items:
            # Add tag to items
            item['type'] = 'movie'
        return dir_items


    @logged_function
    def get_single_tvshow(self, directory, showtitle):
        """Get the single TV show in the directory, and tag the items."""
        show_items = self.filter_blocked_items(
            list(load_directory_items(
                progressdialog=None,
                _path=directory,
                recursive=True,
                sync_type='tvshow'
                )), _type='episode'
            )
        for item in show_items:
            # Add tag to items
            # TODO: this loop aparently not realy work
            item['type'] = 'tvshow'
            item['showtitle'] = showtitle
        return show_items


    @logged_function
    def get_tvshows_in_directory(self, directory):
        """Get all TV shows in the directory, and tag the items."""
        dir_items = self.filter_blocked_items(
            list(load_directory_items(
                progressdialog=None,
                _path=directory,
                allow_directories=True,
                recursive=True,
                sync_type='tvshow'
                )), _type='tvshow'
            )
        all_items = []
        # Check every tvshow in list
        for jsonitem in dir_items:
            showtitle = jsonitem['label']
            # Load results if show isn't blocked
            show_path = jsonitem['file']
            show_items = self.filter_blocked_items(
                list(load_directory_items(
                    progressdialog=None,
                    _path=show_path,
                    recursive=True,
                    sync_type='tvshow'
                    )), _type='episode'
                )
            for show_item in show_items:
                # Add formatted item
                show_item['type'] = 'tvshow'
                show_item['showtitle'] = showtitle
            all_items += show_items
        return all_items


    def options(self, item):
        """Provide options for a single synced directory in a dialog window."""
        # TODO: Remove all from plugin
        # TODO: Rename label
        STR_REMOVE = getlocalizedstring(32017)
        STR_SYNCED_DIR_OPTIONS = getlocalizedstring(32085)
        STR_BACK = getlocalizedstring(32011)
        lines = [STR_REMOVE, STR_BACK]
        ret = xbmcgui.Dialog().select(
            '{0} - {1} - {2}'.format(ADDON_NAME, STR_SYNCED_DIR_OPTIONS, item['label']), lines
        )
        if ret >= 0:
            if lines[ret] == STR_REMOVE:
                self.database.remove_synced_dir(item['dir'])
            elif lines[ret] == STR_BACK:
                pass
        self.view()


    def remove_all(self):
        """Remove all synced directories."""
        STR_REMOVE_ALL_SYNCED_DIRS = getlocalizedstring(32086)
        STR_ALL_SYNCED_DIRS_REMOVED = getlocalizedstring(32087)
        STR_ARE_YOU_SURE = getlocalizedstring(32088)
        if xbmcgui.Dialog().yesno('{0} - {1}'.format(ADDON_NAME, STR_REMOVE_ALL_SYNCED_DIRS),
                                  STR_ARE_YOU_SURE):
            self.database.remove_all_synced_dirs()
            notification(STR_ALL_SYNCED_DIRS_REMOVED)


    def remove_paths(self, paths_to_remove):
        """Remove and delete all items with the given paths."""
        for path in paths_to_remove:
            item = self.database.load_item(path)
            item.remove_from_library()
            item.delete()


    def stage_items(self, items_to_stage):
        """Stage all items in the list."""
        for item in items_to_stage:
            self.database.add_content_item(*item)


    @logged_function
    def add_single_movie(self, title, year, file):
        """Sync single movie path and stage item."""
        STR_MOVIE_STAGED = getlocalizedstring(32105)
        STR_ITEM_IS_ALREADY_STAGED = getlocalizedstring(32103)
        STR_ITEM_IS_ALREADY_MANAGED = getlocalizedstring(32104)
        # Add synced directory to database
        # TODO: add single-movie to synced is necessary? revise this
        self.database.add_synced_dir(title, file, 'single-movie')
        # Check for duplicate in database
        exist_in_db = self.database.path_exists(file=file)
        if exist_in_db == 'staged':
            notification(STR_ITEM_IS_ALREADY_STAGED)
        elif exist_in_db == 'managed':
            notification(STR_ITEM_IS_ALREADY_MANAGED)
        else:
            # Add item to database
            item = build_json_item([file, title, 'movie', None, year])
            self.database.add_content_item(build_contentitem(item))
            notification('%s: %s' % (
                STR_MOVIE_STAGED,
                title_with_color(title, year)
                )
            )


    @logged_function
    def add_single_tvshow(self, title, year, file):
        """Sync single tvshow directory and stage items."""
        STR_i_NEW = getlocalizedstring(32107)
        STR_i_NEW_i_STAGED_i_MANAGED = getlocalizedstring(32106)
        STR_GETTING_ITEMS_IN_DIR = getlocalizedstring(32125)
        # STR_GETTING_ITEMS_IN_x = getlocalizedstring(32126)
        self.progressdialog.create(ADDON_NAME)
        # Add synced directory to database
        self.database.add_synced_dir(
            title,
            file,
            'single-tvshow'
        )
        # Get everything inside tvshow path
        files_list = list(load_directory_items(
            progressdialog=self.progressdialog,
            _path=file,
            allow_directories=True,
            recursive=True,
            year=year,
            showtitle=title,
            sync_type='tvshow'
            )
        )
        # Get all items to stage
        items_to_stage = 0
        num_already_staged = 0
        num_already_managed = 0
        self.progressdialog.update(0, STR_GETTING_ITEMS_IN_DIR)
        for index, jsonitem in enumerate(files_list):
            if self.progressdialog.iscanceled() is True:
                self.progressdialog.close()
                break
            try:
                contentitem = build_contentitem(jsonitem)
                # Update progress
                percent = 100 * index / len(files_list)
                exist_in_db = self.database.path_exists(file=contentitem['file'])
                if 'staged' in exist_in_db:
                    num_already_staged += 1
                    continue
                elif 'managed' in exist_in_db:
                    num_already_managed += 1
                    continue
                elif self.database.check_blocked(contentitem['showtitle'], 'episode'):
                    continue
                # Update progress
                self.progressdialog.update(
                    int(percent),
                    '\n'.join(
                        [
                            title_with_color(
                                contentitem['showtitle'],
                                year=contentitem['year']
                            ),
                                contentitem['episode_title_with_id']
                        ]
                    )
                )
                self.database.add_content_item(contentitem)
                items_to_stage += 1
                xbmc.sleep(300)
            except Exception as e:
                raise e

        if num_already_staged > 0 or num_already_managed > 0:
            notification(
                STR_i_NEW_i_STAGED_i_MANAGED %
                (items_to_stage, num_already_staged, num_already_managed)
            )
        else:
            notification(STR_i_NEW % items_to_stage)


    @logged_function
    def add_all_items_in_directory(self, sync_type, dir_label, dir_path):
        """Synchronize all items in a directory (movies/series or all),
         based on the user's choice and stage items."""
        # TODO: new notification label to show movies,
        #  TV shows and episodes that have been added
        contentitem = None
        content_title = None
        STR_MOVIE_STAGED = getlocalizedstring(32165)
        STR_GETTING_ITEMS_IN_x = getlocalizedstring(32126)
        STR_i_EPISODES_STAGED = getlocalizedstring(32112)
        STR_GETTING_ITEMS_IN_DIR = getlocalizedstring(32125)
        self.progressdialog.create(ADDON_NAME)
        try:
            # add synced directory to database
            # TODO: check it in future
            self.database.add_synced_dir(
                dir_label,
                dir_path,
                'tvshow'
            )
            # query json-rpc to get files in directory
            self.progressdialog.update(0, STR_GETTING_ITEMS_IN_DIR)
            files_list = list(load_directory_items(
                progressdialog=self.progressdialog,
                _path=dir_path,
                allow_directories=True,
                recursive=True,
                sync_type=sync_type))
            items_to_stage = 0
            for index, jsonitem in enumerate(files_list):
                if self.progressdialog.iscanceled() is True:
                    self.progressdialog.close()
                    break
                contentitem = build_contentitem(jsonitem)
                if 'title' in contentitem:
                    content_title = contentitem['title']
                if 'showtitle' in contentitem:
                    content_title = contentitem['showtitle']
                if self.database.check_blocked(content_title, contentitem['type']):
                    continue
                if self.database.path_exists(file=contentitem['file']):
                    continue
                # Update progress
                percent = 100 * index / len(files_list)
                # Check for duplicate paths and blocked items
                try:
                    self.progressdialog.update(
                        int(percent),
                        '\n'.join([STR_GETTING_ITEMS_IN_x % contentitem['showtitle'],
                        contentitem['episode_title_with_id']])
                        )
                    # try add tvshow
                    self.database.add_content_item(
                        contentitem,
                    )
                    xbmc.sleep(300)
                except KeyError:
                    # TODO: new dialog str to movie
                    self.progressdialog.update(
                        int(percent), STR_MOVIE_STAGED % content_title,
                    )
                    # try add movie
                    self.database.add_content_item(
                        contentitem,
                    )
                    xbmc.sleep(500)
                items_to_stage += 1
            notification(STR_i_EPISODES_STAGED % items_to_stage)
        finally:
            self.progressdialog.close()


    def update_all(self):
        """Get all items from synced directories, and
        find unavailable items to remove from managed,
        and new items to stage."""
        # TODO: bugfix: single-movies won't actually get removed if they become unavailable
        #       maybe load parent dir and check for path or label?  it would be slower though
        # TODO: option to only update specified or managed items
        # TODO: option to add update frequencies for specific directories (i.e. weekly/monthly/etc.)
        # TODO: better error handling when plugins dont load during update
        STR_FINDING_ITEMS_TO_REMOVE = getlocalizedstring(32090)
        STR_FINDING_ITEMS_TO_ADD = getlocalizedstring(32092)
        STR_i_TO_REMOVE_i_TO_STAGE_PROCEED = getlocalizedstring(32093)
        STR_REMOVING_ITEMS = getlocalizedstring(32094)
        STR_STAGING_ITEMS = getlocalizedstring(32095)
        STR_ALL_ITEMS_UPTODATE = getlocalizedstring(32121)
        STR_SUCCESS = getlocalizedstring(32122)
        self.progressdialog = xbmcgui.DialogProgressBG()
        self.progressdialog.create(ADDON_NAME)
        try:
            # Get current items in all directories
            synced_dirs = self.database.get_synced_dirs()
            all_items = []
            for index, synced_dir in enumerate(synced_dirs):
                self.progressdialog.update(
                    99 * index / len(synced_dirs),
                    '{label} - {type}'.format(
                        label=synced_dir['label'], type=synced_dir.localize_type()
                    )
                )
                if synced_dir['type'] == 'single-movie':
                    # Directory is just a path to a single movie
                    all_items.append({
                        'file': synced_dir['dir'],
                        'label': synced_dir['label'],
                        'type': 'movie'
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
            self.progressdialog.update(99, STR_FINDING_ITEMS_TO_REMOVE)
            all_paths = [x['file'] for x in all_items]
            paths_to_remove = self.find_paths_to_remove(all_paths)
            # Find dir_items not in managed_items or staged_items, and prepare to add
            self.progressdialog.update(99, STR_FINDING_ITEMS_TO_ADD)
            items_to_stage = self.find_items_to_stage(all_items)
            # Prompt user to remove & stage
            if paths_to_remove or items_to_stage:
                if xbmcgui.Dialog().yesno(
                        ADDON_NAME,
                        STR_i_TO_REMOVE_i_TO_STAGE_PROCEED % (
                            len(paths_to_remove),
                            len(items_to_stage))):
                    if paths_to_remove:
                        self.progressdialog.update(99, STR_REMOVING_ITEMS)
                        self.remove_paths(paths_to_remove)
                    if items_to_stage:
                        self.progressdialog.update(99, STR_STAGING_ITEMS)
                        self.stage_items(items_to_stage)
                    # TODO: update/clean managed folder
                    xbmcgui.Dialog().ok(ADDON_NAME, STR_SUCCESS)
            else:
                xbmcgui.Dialog().ok(ADDON_NAME, STR_ALL_ITEMS_UPTODATE)
        finally:
            self.progressdialog.close()


    def update_movies(self):
        """Update all synced movie directories."""
        STR_FINDING_ITEMS_TO_REMOVE = getlocalizedstring(32090)
        STR_FINDING_ITEMS_TO_ADD = getlocalizedstring(32092)
        STR_i_TO_REMOVE_i_TO_STAGE_PROCEED = getlocalizedstring(32093)
        STR_REMOVING_ITEMS = getlocalizedstring(32094)
        STR_STAGING_ITEMS = getlocalizedstring(32095)
        STR_ALL_ITEMS_UPTODATE = getlocalizedstring(32121)
        STR_SUCCESS = getlocalizedstring(32122)
        self.progressdialog = xbmcgui.DialogProgressBG()
        self.progressdialog.create(ADDON_NAME)
        try:
            all_items = []
            movie_dirs = self.database.get_synced_dirs(synced_type='movie')
            single_movie_dirs = self.database.get_synced_dirs(synced_type='single-movie')
            total_num_dirs = len(movie_dirs + single_movie_dirs)
            for index, synced_dir in enumerate(movie_dirs):
                self.progressdialog.update(
                    int(99 * index / total_num_dirs), synced_dir['label']
                    )
                all_items += self.get_movies_in_directory(synced_dir['file'])
            for index, synced_dir in enumerate(single_movie_dirs):
                self.progressdialog.update(
                    int(99 * (index + len(movie_dirs)) / total_num_dirs),
                    synced_dir['label']
                )
                all_items.append({
                    'file': synced_dir['file'],
                    'label': synced_dir['label'],
                    'type': 'movie'
                })
            # Find managed paths not in dir_items, and prepare to remove
            self.progressdialog.update(99, STR_FINDING_ITEMS_TO_REMOVE)
            all_paths = [x['file'] for x in all_items]
            paths_to_remove = self.find_paths_to_remove(all_paths, type='movie')
            # Find dir_items not in managed_items or staged_items, and prepare to add
            self.progressdialog.update(99, STR_FINDING_ITEMS_TO_ADD)
            items_to_stage = self.find_items_to_stage(all_items)
            # Prompt user to remove & stage
            if paths_to_remove or items_to_stage:
                if xbmcgui.Dialog().yesno(
                        ADDON_NAME,
                        STR_i_TO_REMOVE_i_TO_STAGE_PROCEED % (
                            len(paths_to_remove),
                            len(items_to_stage))):
                    if paths_to_remove:
                        self.progressdialog.update(99, STR_REMOVING_ITEMS)
                        self.remove_paths(paths_to_remove)
                    if items_to_stage:
                        self.progressdialog.update(99, STR_STAGING_ITEMS)
                        self.stage_items(items_to_stage)
                    # TODO: update/clean managed folder
                    xbmcgui.Dialog().ok(ADDON_NAME, STR_SUCCESS)
            else:
                xbmcgui.Dialog().ok(ADDON_NAME, STR_ALL_ITEMS_UPTODATE)
        finally:
            self.progressdialog.close()


    def update_tvshows(self):
        """Update all TV show directories."""
        STR_FINDING_ITEMS_TO_REMOVE = getlocalizedstring(32090)
        STR_FINDING_ITEMS_TO_ADD = getlocalizedstring(32092)
        STR_i_TO_REMOVE_i_TO_STAGE_PROCEED = getlocalizedstring(32093)
        STR_REMOVING_ITEMS = getlocalizedstring(32094)
        STR_STAGING_ITEMS = getlocalizedstring(32095)
        STR_ALL_ITEMS_UPTODATE = getlocalizedstring(32121)
        STR_SUCCESS = getlocalizedstring(32122)
        self.progressdialog.create(ADDON_NAME)
        try:
            all_items = []
            show_dirs = self.database.get_synced_dirs(synced_type='tvshow')
            single_show_dirs = self.database.get_synced_dirs(synced_type='single-tvshow')
            total_num_dirs = len(show_dirs + single_show_dirs)
            for index, synced_dir in enumerate(show_dirs):
                self.progressdialog.update(
                    int(99 * index / total_num_dirs),
                    synced_dir['label']
                )
                all_items += self.get_tvshows_in_directory(synced_dir['file'])
            for index, synced_dir in enumerate(single_show_dirs):
                self.progressdialog.update(
                    int(99. * (index + len(show_dirs)) / total_num_dirs),
                    synced_dir['label']
                )
                all_items += self.get_single_tvshow(
                    synced_dir['file'],
                    synced_dir['label']
                )
            # Find managed paths not in dir_items, and prepare to remove
            self.progressdialog.update(99, STR_FINDING_ITEMS_TO_REMOVE)
            all_paths = [x['file'] for x in all_items]
            paths_to_remove = self.find_paths_to_remove(all_paths, type='tvshow')
            # Find dir_items not in managed_items or staged_items, and prepare to add
            self.progressdialog.update(99, STR_FINDING_ITEMS_TO_ADD)
            items_to_stage = self.find_items_to_stage(all_items)
            # Prompt user to remove & stage
            if paths_to_remove or items_to_stage:
                if xbmcgui.Dialog().yesno(ADDON_NAME, STR_i_TO_REMOVE_i_TO_STAGE_PROCEED %
                                          (len(paths_to_remove), len(items_to_stage))):
                    if paths_to_remove:
                        self.progressdialog.update(99, STR_REMOVING_ITEMS)
                        self.remove_paths(paths_to_remove)
                    if items_to_stage:
                        self.progressdialog.update(99, STR_STAGING_ITEMS)
                        self.stage_items(items_to_stage)
                    # TODO: update/clean managed folder
                    xbmcgui.Dialog().ok(ADDON_NAME, STR_SUCCESS)
            else:
                xbmcgui.Dialog().ok(ADDON_NAME, STR_ALL_ITEMS_UPTODATE)
        finally:
            self.progressdialog.close()


    @logged_function
    def view(self):
        """Display all synced directories, which are selectable and lead to options.
        Also provides additional options at bottom of menu."""
        STR_UPDATE_ALL = getlocalizedstring(32081)
        STR_UPDATE_TV_SHOWS = getlocalizedstring(32137)
        STR_UPDATE_MOVIES = getlocalizedstring(32138)
        STR_REMOVE_ALL = getlocalizedstring(32082)
        STR_BACK = getlocalizedstring(32011)
        STR_SYNCED_DIRECTORIES = getlocalizedstring(32128)
        STR_NO_SYNCED_DIRS = getlocalizedstring(32120)
        synced_dirs = self.database.get_synced_dirs()
        if not synced_dirs:
            xbmcgui.Dialog().ok(
                ADDON_NAME,
                STR_NO_SYNCED_DIRS
                )
            return
        lines = [
            '[B]%s[/B] - %s - [I]%s[/I]' %
            (x['label'], x.localize_type(), x['dir']) for x in synced_dirs
        ]
        lines += [STR_UPDATE_ALL, STR_UPDATE_MOVIES, STR_UPDATE_TV_SHOWS, STR_REMOVE_ALL, STR_BACK]
        ret = xbmcgui.Dialog().select(
            '{0} - {1}'.format(ADDON_NAME, STR_SYNCED_DIRECTORIES), lines
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
