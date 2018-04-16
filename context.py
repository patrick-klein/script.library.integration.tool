#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
This module gets called from the context menu item "Add selected item to library" (32000).
The purpose is to stage the currently selected movie/tvshow, and update synced.pkl.
'''

import os
import sys
import simplejson as json
import xbmc
import xbmcgui
import xbmcaddon

from resources.lib.utils import notification, log_msg
from resources.lib.database_handler import DB_Handler

if __name__ == '__main__':

    addon = xbmcaddon.Addon()
    STR_ADDON_NAME = addon.getAddonInfo('name')
    MANAGED_FOLDER = addon.getSetting('managed_folder')

    # define localized strings for readability
    STR_CHOOSE_FOLDER = addon.getLocalizedString(32123)
    STR_CHOOSE_CONTENT_TYPE = addon.getLocalizedString(32100)
    STR_TV_SHOW = addon.getLocalizedString(32101)
    STR_MOVIE = addon.getLocalizedString(32102)
    STR_ITEM_IS_ALREADY_STAGED = addon.getLocalizedString(32103)
    STR_ITEM_IS_ALREADY_MANAGED = addon.getLocalizedString(32104)
    STR_MOVIE_STAGED = addon.getLocalizedString(32105)
    STR_i_NEW_i_STAGED_i_MANAGED = addon.getLocalizedString(32106)
    STR_i_NEW = addon.getLocalizedString(32107)

    # Display an error is user hasn't configured managed folder yet
    if not (MANAGED_FOLDER and os.path.isdir(MANAGED_FOLDER)):
        notification(STR_CHOOSE_FOLDER)
        log_msg('No managed folder!', xbmc.LOGERROR)
        sys.exit()

    # update .pkl files if present
    if any(['.pkl' in x for x in os.listdir(MANAGED_FOLDER)]):
        import resources.lib.update_pkl
        resources.lib.update_pkl.main()

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

    # create database handler
    dbh = DB_Handler()

    # stage single item for movie
    if content_type == 'movie':

        # get content info
        title = sys.listitem.getLabel()
        path = sys.listitem.getPath()

        # add synced directory to database
        dbh.add_synced_dir(title, path, 'single-movie')

        # check for duplicate in database
        if dbh.path_exists(path, 'staged'):
            notification(STR_ITEM_IS_ALREADY_STAGED)
        elif dbh.path_exists(path, 'managed'):
            notification(STR_ITEM_IS_ALREADY_MANAGED)
        else:
            # add item to database
            dbh.add_content_item(path, title, content_type)
            notification(STR_MOVIE_STAGED)

    # stage multiple episodes for tvshow
    elif content_type == 'tvshow':
        #TODO: progress bar

        # get name and path of tvshow
        tvshow_label = sys.listitem.getLabel()
        tvshow_path = sys.listitem.getPath()

        # add synced directory to database
        dbh.add_synced_dir(tvshow_label, tvshow_path, 'single-tvshow')

        # get everything inside tvshow path
        results = json.loads(xbmc.executeJSONRPC(
            '{"jsonrpc": "2.0", "method": "Files.GetDirectory", \
            "params": {"directory":"%s"}, "id": 1}' % tvshow_path))
        if results.has_key('result'):
            dir_items = results["result"]["files"]
        else:
            dir_items = []

        # get all items to stage
        items_to_stage = 0
        num_already_staged = 0
        num_already_managed = 0
        for ditem in dir_items:
            label = ditem['label']
            path = ditem['file']
            if dbh.path_exists(path, 'staged'):
                num_already_staged += 1
                continue
            elif dbh.path_exists(path, 'managed'):
                num_already_managed += 1
                continue
            elif dbh.check_blocked(label, 'episode'):
                continue
            #TODO: get episode id and airdate
            dbh.add_content_item(path, label, content_type, tvshow_label)
            items_to_stage += 1

        if num_already_staged > 0 or num_already_managed > 0:
            notification(STR_i_NEW_i_STAGED_i_MANAGED % \
                (items_to_stage, num_already_staged, num_already_managed))
        else:
            notification(STR_i_NEW % items_to_stage)
