#!/usr/bin/python
# -*- coding: utf-8 -*-

'''Defines the SyncedMenu class'''

# TODO: Different notifications depending on whether items were staged vs. automatically added
import sys

import xbmc # pylint: disable=import-error
import xbmcgui # pylint: disable=import-error


from resources import ADDON_NAME

from resources.lib.log import logged_function

from resources.lib.items.movie import MovieItem
from resources.lib.items.episode import EpisodeItem

from resources.lib.utils import notification
from resources.lib.utils import title_with_color
from resources.lib.utils import getlocalizedstring
from resources.lib.utils import load_directory_items

from resources.lib.database_handler import DatabaseHandler


class SyncedMenu(object):
    '''Provides windows for displaying synced directories,
    and tools for managing them and updating their contents'''

    # IDEA: new "find all directories" context item that finds and consolidates directories

    def __init__(self):
        self.dbh = DatabaseHandler()


        '''Filters out all blocked items in the list'''


    @logged_function
    def find_items_to_stage(self, all_items):
        '''Find items in the list not present in database'''
        items_to_stage = []
        item = []
        for dir_item in all_items:
            path = dir_item['file']
            # Don't prepare items that are already staged or managed
            label = dir_item['label']
            mediatype = 'tvshow' if dir_item['mediatype'] == 'episode' else dir_item['mediatype']
            if self.dbh.path_exists(path=path, status=['staged', 'managed'], mediatype=mediatype):
                continue
            if mediatype == 'movie':
                item = (path, label, mediatype)
            elif mediatype == 'tvshow':
                item = (path, label, mediatype, dir_item['show_title'])
            items_to_stage.append(item)
        return items_to_stage


    @logged_function
    def find_paths_to_remove(self, all_paths, **kwargs):
        '''Find paths in database no longer available'''
        #TODO: update this func in future
        managed_items = self.dbh.get_content_items(**kwargs)
        return [x.path for x in managed_items if x.path not in all_paths]


    @logged_function
    def get_movies_in_directory(self, directory):
        '''Get all movies in the directory and tags them'''
        dir_items = self.filter_blocked_items(
            list(load_directory_items(
                progressdialog=None,
                dir_path=directory,
                recursive=True,
                sync_type='movie'
                )), mediatype='movie'
            )
        for item in dir_items:
            # Add tag to items
            item['mediatype'] = 'movie'
        return dir_items


    @logged_function
        '''Get the single TV show in the directory, and tag the items'''
        show_items = self.filter_blocked_items(
            list(load_directory_items(
                progressdialog=None,
                dir_path=directory,
                recursive=True,
                sync_type='tvshow'
                )), mediatype='episode'
            )
        for item in show_items:
            # Add tag to items
            item['mediatype'] = 'tvshow'
            item['show_title'] = show_title
        return show_items


    @logged_function
    def get_tvshows_in_directory(self, directory):
        '''Get all TV shows in the directory, and tag the items'''
        dir_items = self.filter_blocked_items(
            list(load_directory_items(
                progressdialog=None,
                dir_path=directory,
                allow_directories=True,
                recursive=True,
                sync_type='tvshow'
                )), mediatype='tvshow'
            )
        all_items = []
        # Check every tvshow in list
        for dir_item in dir_items:
            show_title = dir_item['label']
            # Load results if show isn't blocked
            show_path = dir_item['file']
            show_items = self.filter_blocked_items(
                list(load_directory_items(
                    progressdialog=None,
                    dir_path=show_path,
                    recursive=True,
                    sync_type='tvshow'
                    )), mediatype='episode'
                )
            for show_item in show_items:
                # Add formatted item
                show_item['mediatype'] = 'tvshow'
                show_item['show_title'] = show_title
            all_items += show_items
        return all_items


    def options(self, item):
        '''Provide options for a single synced directory in a dialog window'''
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
                self.dbh.remove_synced_dir(item['dir'])
            elif lines[ret] == STR_BACK:
                pass
        self.view()


    def remove_all(self):
        '''Remove all synced directories'''
        STR_REMOVE_ALL_SYNCED_DIRS = getlocalizedstring(32086)
        STR_ALL_SYNCED_DIRS_REMOVED = getlocalizedstring(32087)
        STR_ARE_YOU_SURE = getlocalizedstring(32088)
        if xbmcgui.Dialog().yesno('{0} - {1}'.format(ADDON_NAME, STR_REMOVE_ALL_SYNCED_DIRS),
                                  STR_ARE_YOU_SURE):
            self.dbh.remove_all_synced_dirs()
            notification(STR_ALL_SYNCED_DIRS_REMOVED)


    def remove_paths(self, paths_to_remove):
        '''Remove and delete all items with the given paths'''
        for path in paths_to_remove:
            item = self.dbh.load_item(path)
            item.remove_from_library()
            item.delete()


    def stage_items(self, items_to_stage):
        '''Stage all items in the list'''
        for item in items_to_stage:
            self.dbh.add_content_item(*item)


    @logged_function
        '''Sync single movie path and stage item'''
        STR_ITEM_IS_ALREADY_STAGED = getlocalizedstring(32103)
        STR_ITEM_IS_ALREADY_MANAGED = getlocalizedstring(32104)
        STR_MOVIE_STAGED = getlocalizedstring(32105)
        # Add synced directory to database
        self.dbh.add_synced_dir(title, link_stream_path, 'single-movie')
        # Check for duplicate in database
        if self.dbh.path_exists(path=link_stream_path, status='staged', mediatype='movie'):
            notification(STR_ITEM_IS_ALREADY_STAGED)
        elif self.dbh.path_exists(path=link_stream_path, status='managed', mediatype='movie'):
            notification(STR_ITEM_IS_ALREADY_MANAGED)
        else:
            # Add item to database
            self.dbh.add_content_item(MovieItem(
                title=title,
                year=year,
                link_stream_path=link_stream_path,
                mediatype='movie',
                ).returasjson(), 'movie')
            notification('%s: %s' % (
                STR_MOVIE_STAGED,
                title_with_color(title, year)
                ))


    @logged_function
        '''Sync single tvshow directory and stage items'''
        STR_i_NEW_i_STAGED_i_MANAGED = getlocalizedstring(32106)
        STR_i_NEW = getlocalizedstring(32107)
        STR_GETTING_ITEMS_IN_DIR = getlocalizedstring(32125)
        STR_GETTING_ITEMS_IN_x = getlocalizedstring(32126)
        progressdialog = xbmcgui.DialogProgress()
        progressdialog.create(ADDON_NAME)
        # Add synced directory to database
        self.dbh.add_synced_dir(title, link_stream_path, 'single-tvshow')
        # Get everything inside tvshow path
        files_list = list(load_directory_items(
            progressdialog=progressdialog,
            dir_path=link_stream_path,
            allow_directories=True,
            recursive=True,
            year=year,
            showtitle=title,
            sync_type='tvshow'))
        # Get all items to stage
        items_to_stage = 0
        num_already_staged = 0
        num_already_managed = 0
        progressdialog.update(0, STR_GETTING_ITEMS_IN_DIR)
        for index, showfile in enumerate(files_list):
            if progressdialog.iscanceled() is True:
                progressdialog.close()
                break
            try:
                contentdata = EpisodeItem(
                    # IDEA: in future, pass a json and not separeted values
                    link_stream_path=showfile['file'],
                    title=showfile['title'],
                    mediatype='tvshow',
                    show_title=title,
                    season=showfile['season'],
                    epnumber=showfile['episode'],
                    year=year if year else showfile['year']
                ).returasjson()
                # Update progress
                percent = 100 * index / len(files_list)
                if (self.dbh.path_exists(
                        path=contentdata['link_stream_path'],
                        status='staged',
                        mediatype='tvshow')):
                    num_already_staged += 1
                    continue
                elif (self.dbh.path_exists(
                        path=contentdata['link_stream_path'],
                        status='managed',
                        mediatype='tvshow')):
                    num_already_managed += 1
                    continue
                elif self.dbh.check_blocked(contentdata['show_title'], 'episode'):
                    continue
                # Update progress
                progressdialog.update(
                    int(percent),
                    '\n'.join(
                        [
                            title_with_color(
                                contentdata['show_title'],
                                year=contentdata['year']
                            ),
                                contentdata['episode_title_with_id']
                        ]
                    )
                )
                self.dbh.add_content_item(contentdata, 'tvshow')
                items_to_stage += 1
                xbmc.sleep(300)
            except TypeError:
                notification(
                    getlocalizedstring(32166),
                    4000
                )
        if num_already_staged > 0 or num_already_managed > 0:
            notification(
                STR_i_NEW_i_STAGED_i_MANAGED %
                (items_to_stage, num_already_staged, num_already_managed)
            )
        else:
            notification(STR_i_NEW % items_to_stage)


    @logged_function
        '''Synchronize all items in a directory (movies/series or all),
         based on the user's choice and stage items'''
        # TODO: new notification label to show movies,
        #  TV shows and episodes that have been added
        contentdata = None
        content_title = None
        STR_GETTING_ITEMS_IN_DIR = getlocalizedstring(32125)
        STR_GETTING_ITEMS_IN_x = getlocalizedstring(32126)
        STR_i_EPISODES_STAGED = getlocalizedstring(32112)
        STR_MOVIE_STAGED = getlocalizedstring(32165)
        progressdialog = xbmcgui.DialogProgress()
        progressdialog.create(ADDON_NAME)
        try:
            # add synced directory to database
            # TODO: check it in future
            self.dbh.add_synced_dir(dir_label, dir_path, 'tvshow')
            # query json-rpc to get files in directory
            progressdialog.update(0, STR_GETTING_ITEMS_IN_DIR)
            files_list = list(load_directory_items(
                progressdialog=progressdialog,
                dir_path=dir_path,
                allow_directories=True,
                recursive=True,
                sync_type=sync_type))
            items_to_stage = 0
            for index, content_file in enumerate(files_list):
                if progressdialog.iscanceled() is True:
                    progressdialog.close()
                    break
                try:
                    content_title = content_file['movie_title']
                    contentdata = MovieItem(
                        link_stream_path=content_file['file'],
                        title=content_file['movie_title'],
                        mediatype='movie',
                        year=content_file['year']
                    ).returasjson()
                    sync_type = 'movie'
                except (KeyError, TypeError):
                    content_title = content_file['showtitle']
                    contentdata = EpisodeItem(
                        link_stream_path=content_file['file'],
                        title=content_file['title'],
                        mediatype='tvshow',
                        show_title=content_file['showtitle'],
                        season=content_file['season'],
                        epnumber=content_file['episode'],
                        year=content_file['year']
                    ).returasjson()
                    sync_type = 'tvshow'
                except (KeyError, TypeError) as e:
                    raise e
                # Get name of show and skip if blocked
                # Get everything inside tvshow path
                # # # # # # # # # # # # # # # # # # # # type: movie or episode
                if self.dbh.check_blocked(content_title, content_file['type']):
                    continue
                if self.dbh.path_exists(
                        path=contentdata['link_stream_path'],
                        status=['staged', 'managed'],
                        # TODO: future dosen't use sync_type here
                        mediatype=sync_type):
                    continue
                # Update progress
                percent = 100 * index / len(files_list)
                # Check for duplicate paths and blocked items
                try:
                    progressdialog.update(
                        int(percent),
                        '\n'.join([STR_GETTING_ITEMS_IN_x % contentdata['show_title'],
                        contentdata['episode_title_with_id']])
                        )
                    # try add tvshow
                    self.dbh.add_content_item(contentdata, 'tvshow')
                    xbmc.sleep(300)
                except KeyError:
                    # TODO: new dialog str to movie
                    progressdialog.update(
                        int(percent), STR_MOVIE_STAGED % content_title,
                    )
                    # try add movie
                    self.dbh.add_content_item(contentdata, 'movie')
                    xbmc.sleep(500)
                items_to_stage += 1
            notification(STR_i_EPISODES_STAGED % items_to_stage)
        finally:
            progressdialog.close()


    def update_all(self):
        '''Get all items from synced directories, and
        find unavailable items to remove from managed,
        and new items to stage'''
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
        progressdialog = xbmcgui.DialogProgressBG()
        progressdialog.create(ADDON_NAME)
        try:
            # Get current items in all directories
            synced_dirs = self.dbh.get_synced_dirs()
            all_items = []
            for index, synced_dir in enumerate(synced_dirs):
                progressdialog.update(
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
            progressdialog.update(99, STR_FINDING_ITEMS_TO_REMOVE)
            all_paths = [x['file'] for x in all_items]
            paths_to_remove = self.find_paths_to_remove(all_paths)
            # Find dir_items not in managed_items or staged_items, and prepare to add
            progressdialog.update(99, STR_FINDING_ITEMS_TO_ADD)
            items_to_stage = self.find_items_to_stage(all_items)
            # Prompt user to remove & stage
            if paths_to_remove or items_to_stage:
                if xbmcgui.Dialog().yesno(
                        ADDON_NAME,
                        STR_i_TO_REMOVE_i_TO_STAGE_PROCEED % (
                            len(paths_to_remove),
                            len(items_to_stage))):
                    if paths_to_remove:
                        progressdialog.update(99, STR_REMOVING_ITEMS)
                        self.remove_paths(paths_to_remove)
                    if items_to_stage:
                        progressdialog.update(99, STR_STAGING_ITEMS)
                        self.stage_items(items_to_stage)
                    # TODO: update/clean managed folder
                    xbmcgui.Dialog().ok(ADDON_NAME, STR_SUCCESS)
            else:
                xbmcgui.Dialog().ok(ADDON_NAME, STR_ALL_ITEMS_UPTODATE)
        finally:
            progressdialog.close()


    def update_movies(self):
        '''Update all synced movie directories'''
        STR_FINDING_ITEMS_TO_REMOVE = getlocalizedstring(32090)
        STR_FINDING_ITEMS_TO_ADD = getlocalizedstring(32092)
        STR_i_TO_REMOVE_i_TO_STAGE_PROCEED = getlocalizedstring(32093)
        STR_REMOVING_ITEMS = getlocalizedstring(32094)
        STR_STAGING_ITEMS = getlocalizedstring(32095)
        STR_ALL_ITEMS_UPTODATE = getlocalizedstring(32121)
        STR_SUCCESS = getlocalizedstring(32122)
        progressdialog = xbmcgui.DialogProgressBG()
        progressdialog.create(ADDON_NAME)
        try:
            all_items = []
            movie_dirs = self.dbh.get_synced_dirs(synced_type='movie')
            single_movie_dirs = self.dbh.get_synced_dirs(synced_type='single-movie')
            total_num_dirs = len(movie_dirs + single_movie_dirs)
            for index, synced_dir in enumerate(movie_dirs):
                progressdialog.update(
                    int(99 * index / total_num_dirs), synced_dir['label']
                    )
                all_items += self.get_movies_in_directory(synced_dir['dir'])
            for index, synced_dir in enumerate(single_movie_dirs):
                progressdialog.update(
                    int(99 * (index + len(movie_dirs)) / total_num_dirs),
                    synced_dir['label']
                )
                all_items.append({
                    'file': synced_dir['dir'],
                    'label': synced_dir['label'],
                    'mediatype': 'movie'
                })
            # Find managed paths not in dir_items, and prepare to remove
            progressdialog.update(99, STR_FINDING_ITEMS_TO_REMOVE)
            all_paths = [x['file'] for x in all_items]
            paths_to_remove = self.find_paths_to_remove(all_paths, mediatype='movie')
            # Find dir_items not in managed_items or staged_items, and prepare to add
            progressdialog.update(99, STR_FINDING_ITEMS_TO_ADD)
            items_to_stage = self.find_items_to_stage(all_items)
            # Prompt user to remove & stage
            if paths_to_remove or items_to_stage:
                if xbmcgui.Dialog().yesno(
                        ADDON_NAME,
                        STR_i_TO_REMOVE_i_TO_STAGE_PROCEED % (
                            len(paths_to_remove),
                            len(items_to_stage))):
                    if paths_to_remove:
                        progressdialog.update(99, STR_REMOVING_ITEMS)
                        self.remove_paths(paths_to_remove)
                    if items_to_stage:
                        progressdialog.update(99, STR_STAGING_ITEMS)
                        self.stage_items(items_to_stage)
                    # TODO: update/clean managed folder
                    xbmcgui.Dialog().ok(ADDON_NAME, STR_SUCCESS)
            else:
                xbmcgui.Dialog().ok(ADDON_NAME, STR_ALL_ITEMS_UPTODATE)
        finally:
            progressdialog.close()


    def update_tvshows(self):
        '''Update all TV show directories'''
        STR_FINDING_ITEMS_TO_REMOVE = getlocalizedstring(32090)
        STR_FINDING_ITEMS_TO_ADD = getlocalizedstring(32092)
        STR_i_TO_REMOVE_i_TO_STAGE_PROCEED = getlocalizedstring(32093)
        STR_REMOVING_ITEMS = getlocalizedstring(32094)
        STR_STAGING_ITEMS = getlocalizedstring(32095)
        STR_ALL_ITEMS_UPTODATE = getlocalizedstring(32121)
        STR_SUCCESS = getlocalizedstring(32122)
        progressdialog = xbmcgui.DialogProgressBG()
        progressdialog.create(ADDON_NAME)
        try:
            all_items = []
            show_dirs = self.dbh.get_synced_dirs(synced_type='tvshow')
            single_show_dirs = self.dbh.get_synced_dirs(synced_type='single-tvshow')
            total_num_dirs = len(show_dirs + single_show_dirs)
            for index, synced_dir in enumerate(show_dirs):
                progressdialog.update(
                    int(99 * index / total_num_dirs), synced_dir['label']
                    )
                all_items += self.get_tvshows_in_directory(synced_dir['dir'])
            for index, synced_dir in enumerate(single_show_dirs):
                progressdialog.update(
                    int(99. * (index + len(show_dirs)) / total_num_dirs),
                    synced_dir['label']
                )
                all_items += self.get_single_tvshow(synced_dir['dir'], synced_dir['label'])
            # Find managed paths not in dir_items, and prepare to remove
            progressdialog.update(99, STR_FINDING_ITEMS_TO_REMOVE)
            all_paths = [x['file'] for x in all_items]
            paths_to_remove = self.find_paths_to_remove(all_paths, mediatype='tvshow')
            # Find dir_items not in managed_items or staged_items, and prepare to add
            progressdialog.update(99, STR_FINDING_ITEMS_TO_ADD)
            items_to_stage = self.find_items_to_stage(all_items)
            # Prompt user to remove & stage
            if paths_to_remove or items_to_stage:
                if xbmcgui.Dialog().yesno(ADDON_NAME, STR_i_TO_REMOVE_i_TO_STAGE_PROCEED %
                                          (len(paths_to_remove), len(items_to_stage))):
                    if paths_to_remove:
                        progressdialog.update(99, STR_REMOVING_ITEMS)
                        self.remove_paths(paths_to_remove)
                    if items_to_stage:
                        progressdialog.update(99, STR_STAGING_ITEMS)
                        self.stage_items(items_to_stage)
                    # TODO: update/clean managed folder
                    xbmcgui.Dialog().ok(ADDON_NAME, STR_SUCCESS)
            else:
                xbmcgui.Dialog().ok(ADDON_NAME, STR_ALL_ITEMS_UPTODATE)
        finally:
            progressdialog.close()


    @logged_function
    def view(self):
        '''Display all synced directories, which are selectable and lead to options.
        Also provides additional options at bottom of menu'''
        STR_UPDATE_ALL = getlocalizedstring(32081)
        STR_UPDATE_TV_SHOWS = getlocalizedstring(32137)
        STR_UPDATE_MOVIES = getlocalizedstring(32138)
        STR_REMOVE_ALL = getlocalizedstring(32082)
        STR_BACK = getlocalizedstring(32011)
        STR_SYNCED_DIRECTORIES = getlocalizedstring(32128)
        STR_NO_SYNCED_DIRS = getlocalizedstring(32120)
        synced_dirs = self.dbh.get_synced_dirs()
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
