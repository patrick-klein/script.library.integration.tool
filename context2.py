#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
This module gets called from the context menu item "Sync directory to library" (32001).
The purpose is to stage all movies/tvshows in the current directory, and update synced.pkl
'''

import sys
import xbmc
import xbmcgui
import xbmcaddon

import simplejson as json

from resources.lib.contentitem import MovieItem, EpisodeItem
from resources.lib.utils import get_items, save_items, notification, log_msg

if __name__ == '__main__':
    #TODO: add recursive option
    #TODO: fix for empty directories

    addon = xbmcaddon.Addon()
    STR_ADDON_NAME = addon.getAddonInfo('name')

    # Display an error is user hasn't configured managed folder yet
    if not addon.getSetting('managed_folder'):
        STR_CHOOSE_FOLDER = addon.getLocalizedString(32123)
        notification(STR_CHOOSE_FOLDER)
        log_msg('No managed folder!', xbmc.LOGERROR)
        sys.exit()

    # define localized strings for readability
    STR_CHOOSE_CONTENT_TYPE = addon.getLocalizedString(32100)
    STR_TV_SHOWS = addon.getLocalizedString(32108)
    STR_MOVIES = addon.getLocalizedString(32109)
    STR_ALREADY_SYNCED = addon.getLocalizedString(32110)
    STR_i_MOVIES_STAGED = addon.getLocalizedString(32111)
    STR_i_EPISODES_STAGED = addon.getLocalizedString(32112)
    STR_UPDATING_SYNCED_FILE = addon.getLocalizedString(32124)
    STR_GETTING_ITEMS_IN_DIR = addon.getLocalizedString(32125)
    STR_GETTING_ITEMS_IN_x = addon.getLocalizedString(32126)

    # get content type
    container_type = xbmc.getInfoLabel('Container.Content')
    if container_type == 'movies':
        # check if contents are movie
        content_type = "movie"
    else:
        # ask user otherwise
        is_show = xbmcgui.Dialog().yesno(
            STR_ADDON_NAME, STR_CHOOSE_CONTENT_TYPE,
            yeslabel=STR_TV_SHOWS, nolabel=STR_MOVIES)
        if is_show:
            content_type = 'tvshow'
        else:
            content_type = 'movie'

    pDialog = xbmcgui.DialogProgress()
    pDialog.create(STR_ADDON_NAME)

    # update synced file
    #TODO: add label to 'movie' and 'tvshow' types
    pDialog.update(0, line1=STR_UPDATING_SYNCED_FILE)
    synced_dirs = get_items('synced.pkl')
    current_dir = {'dir':xbmc.getInfoLabel('Container.FolderPath'), 'mediatype':content_type}
    if current_dir not in synced_dirs:
        synced_dirs.append(current_dir)
        log_msg('sync: %s' % current_dir)
    save_items('synced.pkl', synced_dirs)

    # query json-rpc to get files in directory
    # TODO: try xbmcvfs.listdir(path) instead
    pDialog.update(0, line1=STR_GETTING_ITEMS_IN_DIR)
    results = xbmc.executeJSONRPC(
        '{"jsonrpc": "2.0", "method": "Files.GetDirectory", \
        "params": {"directory":"%s"}, "id": 1}' % current_dir['dir'])
    dir_items = json.loads(results)["result"]["files"]
    log_msg('dir_items: %s' % dir_items, xbmc.LOGNOTICE)

    if content_type == 'movie':

        # loop through all items and get titles and paths and stage them
        staged_items = get_items('staged.pkl')
        staged_paths = [x.get_path() for x in staged_items]
        managed_paths = [x.get_path() for x in get_items('managed.pkl')]
        blocked_items = get_items('blocked.pkl')
        blocked_movies = [x['label'] for x in blocked_items if x['type'] == 'movie']
        blocked_keywords = [x['label'].lower() for x in blocked_items if x['type'] == 'keyword']
        items_to_stage = []
        for i, ditem in enumerate(dir_items):
            # get label & path for item
            label = ditem['label']
            path = ditem['file']
            # update progress
            pDialog.update(0, line2=label)
            # check for duplicate paths
            if (path in staged_paths) or (path in managed_paths):
                continue
            # check for blocked items
            if label in blocked_movies or any(x in label.lower() for x in blocked_keywords):
                continue
            # create ContentItem
            item = MovieItem(path, label, content_type)
            # add to staged
            items_to_stage.append(item)
            pDialog.update(0, line2=' ')
        staged_items += items_to_stage
        save_items('staged.pkl', staged_items)
        pDialog.close()
        notification(STR_i_MOVIES_STAGED % len(items_to_stage))


    elif content_type == 'tvshow':
        #TODO: add fix for smithsonian, so you can add from episode directory

        staged_items = get_items('staged.pkl')
        staged_paths = [x.get_path() for x in staged_items]
        managed_paths = [x.get_path() for x in get_items('managed.pkl')]
        blocked_items = get_items('blocked.pkl')
        blocked_shows = [x['label'] for x in blocked_items if x['type'] == 'tvshow']
        blocked_episodes = [x['label'] for x in blocked_items if x['type'] == 'episode']
        blocked_keywords = [x['label'].lower() for x in blocked_items if x['type'] == 'keyword']
        items_to_stage = []
        for ditem in dir_items:
            # get name of show and skip if blocked
            tvshow_label = ditem['label']
            if tvshow_label in blocked_shows or \
                any(x in tvshow_label.lower() for x in blocked_keywords):
                continue
            # update progress
            pDialog.update(0, line1=(STR_GETTING_ITEMS_IN_x % tvshow_label))
            # get everything inside tvshow path
            tvshow_path = ditem['file']
            results = json.loads(xbmc.executeJSONRPC(
                '{"jsonrpc": "2.0", "method": "Files.GetDirectory", \
                "params": {"directory":"%s"}, "id": 1}' % tvshow_path))
            if not results.has_key('result'):
                continue
            if not results["result"].has_key('files'):
                continue
            show_items = results["result"]["files"]
            # get all items to stage in show
            for shitem in show_items:
                # get label and path
                label = shitem['label']
                path = shitem['file']
                # update progress
                pDialog.update(0, line2=label)
                # check if already managed or staged
                if path in staged_paths:
                    continue
                elif path in managed_paths:
                    continue
                elif label in blocked_episodes or \
                    any(x in tvshow_label.lower() for x in blocked_keywords):
                    continue
                item = EpisodeItem(path, shitem['label'], content_type, tvshow_label)
                items_to_stage.append(item)
                pDialog.update(0, line2=' ')
            pDialog.update(0, line1=' ')
        # add all items from all shows to stage list
        staged_items += items_to_stage
        save_items('staged.pkl', staged_items)
        pDialog.close()
        notification(STR_i_EPISODES_STAGED % len(items_to_stage))
