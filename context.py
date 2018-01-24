#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
This module gets called from the context menu item "Add selected item to library" (32000).
The purpose is to stage the currently selected movie/tvshow, and update synced.pkl.
'''

import sys
import xbmc
import xbmcgui
import xbmcaddon

import simplejson as json

from resources.lib.contentitem import MovieItem, EpisodeItem
from resources.lib.utils import get_items, save_items, notification, log_msg

if __name__ == '__main__':
    #TODO: don't add items already in library

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
    STR_TV_SHOW = addon.getLocalizedString(32101)
    STR_MOVIE = addon.getLocalizedString(32102)
    STR_ITEM_IS_ALREADY_STAGED = addon.getLocalizedString(32103)
    STR_ITEM_IS_ALREADY_MANAGED = addon.getLocalizedString(32104)
    STR_MOVIE_STAGED = addon.getLocalizedString(32105)
    STR_i_NEW_i_STAGED_i_MANAGED = addon.getLocalizedString(32106)
    STR_i_NEW = addon.getLocalizedString(32107)

    # get content type
    container_type = xbmc.getInfoLabel('Container.Content')
    if container_type == 'tvshows':
        # if listitem is folder, it must be a tv show
        content_type = "tvshow"
    elif container_type == 'movies':
        # check if contents are movie
        content_type = "movie"
    else:
        # ask user otherwise
        is_show = xbmcgui.Dialog().yesno(
            STR_ADDON_NAME, STR_CHOOSE_CONTENT_TYPE,
            yeslabel=STR_TV_SHOW, nolabel=STR_MOVIE)
        if is_show:
            content_type = 'tvshow'
        else:
            content_type = 'movie'

    # stage single item for movie
    if content_type == 'movie':

        # get content info
        label = sys.listitem.getLabel()
        path = sys.listitem.getPath()

        # update synced file
        synced_dirs = get_items('synced.pkl')
        folder_path = xbmc.getInfoLabel('Container.FolderPath')
        movie_dir = {'dir':path, 'mediatype':'single-movie', 'label':label}
        if (movie_dir not in synced_dirs) and ({'dir': folder_path, 'mediatype':'movie'} not in synced_dirs):
            synced_dirs.append(movie_dir)
            save_items('synced.pkl', synced_dirs)
            log_msg('sync: %s' % movie_dir)

        # prepare to stage
        staged_items = get_items('staged.pkl')
        staged_paths = [x.get_path() for x in staged_items]
        managed_paths = [x.get_path() for x in get_items('managed.pkl')]

        # check for duplicate
        if path in staged_paths:
            notification(STR_ITEM_IS_ALREADY_STAGED)
        elif path in managed_paths:
            notification(STR_ITEM_IS_ALREADY_MANAGED)
        else:
            # stage item
            item = MovieItem(path, label, content_type)
            staged_items.append(item)
            save_items('staged.pkl', staged_items)
            notification(STR_MOVIE_STAGED)

    # stage multiple episodes for tvshow
    elif content_type == 'tvshow':
        #TODO: progress bar

        # get name and path of tvshow
        tvshow_label = sys.listitem.getLabel()
        tvshow_path = sys.listitem.getPath()

        # update synced file
        synced_dirs = get_items('synced.pkl')
        folder_path = xbmc.getInfoLabel('Container.FolderPath')
        show_dir = {'dir':tvshow_path, 'mediatype':'single-tvshow', 'label':tvshow_label}
        if (show_dir not in synced_dirs) and ({'dir': folder_path, 'mediatype':'tvshow'} not in synced_dirs):
            synced_dirs.append(show_dir)
            save_items('synced.pkl', synced_dirs)
            log_msg('sync: %s' % show_dir)

        # get everything inside tvshow path
        results = json.loads(xbmc.executeJSONRPC(
            '{"jsonrpc": "2.0", "method": "Files.GetDirectory", \
            "params": {"directory":"%s"}, "id": 1}' % tvshow_path))
        if results.has_key('result'):
            dir_items = results["result"]["files"]
        else:
            dir_items = []
        log_msg('show_items: %s' % dir_items)

        # get all items to stage
        staged_items = get_items('staged.pkl')
        staged_paths = [x.get_path() for x in staged_items]
        managed_paths = [x.get_path() for x in get_items('managed.pkl')]
        blocked_items = get_items('blocked.pkl')
        blocked_episodes = [x['label'] for x in blocked_items if x['type'] == 'episode']
        blocked_keywords = [x['label'].lower() for x in blocked_items if x['type'] == 'keyword']
        items_to_stage = []
        num_already_staged = 0
        num_already_managed = 0
        for ditem in dir_items:
            label = ditem['label']
            path = ditem['file']
            if path in staged_paths:
                num_already_staged += 1
                continue
            elif path in managed_paths:
                num_already_managed += 1
                continue
            elif label in blocked_episodes or any(x in label.lower() for x in blocked_keywords):
                continue
            #TODO: this is where i'd get episode id
            #   consider pulling airdate as well
            item = EpisodeItem(path, label, content_type, tvshow_label)
            items_to_stage.append(item)

        # add all items to stage list
        staged_items += items_to_stage
        save_items('staged.pkl', staged_items)

        if num_already_staged > 0 or num_already_managed > 0:
            notification(STR_i_NEW_i_STAGED_i_MANAGED % \
                (len(items_to_stage), num_already_staged, num_already_managed))
        else:
            notification(STR_i_NEW % len(items_to_stage))
