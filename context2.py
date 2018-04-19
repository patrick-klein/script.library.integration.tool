#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
This module gets called from the context menu item "Sync directory to library" (32001).
The purpose is to stage all movies/tvshows in the current directory, and update synced.pkl
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
    #TODO: add recursive option
    #TODO: let user name/rename directory label

    addon = xbmcaddon.Addon()
    STR_ADDON_NAME = addon.getAddonInfo('name')
    MANAGED_FOLDER = addon.getSetting('managed_folder')

    # define localized strings for readability
    STR_CHOOSE_FOLDER = addon.getLocalizedString(32123)
    STR_CHOOSE_CONTENT_TYPE = addon.getLocalizedString(32100)
    STR_TV_SHOWS = addon.getLocalizedString(32108)
    STR_MOVIES = addon.getLocalizedString(32109)
    STR_ALREADY_SYNCED = addon.getLocalizedString(32110)
    STR_i_MOVIES_STAGED = addon.getLocalizedString(32111)
    STR_i_EPISODES_STAGED = addon.getLocalizedString(32112)
    STR_UPDATING_SYNCED_FILE = addon.getLocalizedString(32124)
    STR_GETTING_ITEMS_IN_DIR = addon.getLocalizedString(32125)
    STR_GETTING_ITEMS_IN_x = addon.getLocalizedString(32126)

    # Display an error is user hasn't configured managed folder yet
    if not (MANAGED_FOLDER and os.path.isdir(MANAGED_FOLDER)):
        notification(STR_CHOOSE_FOLDER)
        log_msg('No managed folder!', xbmc.LOGWARNING)
        sys.exit()

    # update .pkl files if present
    if any(['.pkl' in x for x in os.listdir(MANAGED_FOLDER)]):
        import resources.lib.update_pkl
        resources.lib.update_pkl.main()

    # get content type
    container_type = xbmc.getInfoLabel('Container.Content')
    if container_type == 'movies':
        # check if contents are movie
        content_type = "movie"
    else:
        #TODO: check if path is already in Synced, and get content type there
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

    # create database handler
    dbh = DB_Handler()

    # add synced directory to database
    pDialog.update(0, line1=STR_UPDATING_SYNCED_FILE)
    dir_path = xbmc.getInfoLabel('Container.FolderPath')
    dir_label = xbmc.getInfoLabel('Container.FolderName')
    dbh.add_synced_dir(dir_label, dir_path, content_type)

    # query json-rpc to get files in directory
    # TODO: try xbmcvfs.listdir(path) instead
    pDialog.update(0, line1=STR_GETTING_ITEMS_IN_DIR)
    results = json.loads(xbmc.executeJSONRPC(
        '{"jsonrpc": "2.0", "method": "Files.GetDirectory", \
        "params": {"directory":"%s"}, "id": 1}' % dir_path))
    # halt if results don't load
    if not (results.has_key('result') and results["result"].has_key('files')):
        #TODO: add notification that directory was added but no items
        sys.exit()
    dir_items = results["result"]["files"]

    if content_type == 'movie':

        # loop through all items and get titles and paths and stage them
        items_to_stage = 0
        for i, ditem in enumerate(dir_items):
            # get label & path for item
            label = ditem['label']
            path = ditem['file']
            if dbh.path_exists(path) or dbh.check_blocked(label, 'movie'):
                continue
            # update progress
            pDialog.update(0, line2=label)
            # add item to database
            dbh.add_content_item(path, label, content_type)
            items_to_stage += 1
            pDialog.update(0, line2=' ')
        pDialog.close()
        notification(STR_i_MOVIES_STAGED % items_to_stage)


    elif content_type == 'tvshow':
        #TODO: add fix for smithsonian, so you can add from episode directory

        items_to_stage = 0
        for ditem in dir_items:
            # get name of show and skip if blocked
            tvshow_label = ditem['label']
            if dbh.check_blocked(tvshow_label, 'tvshow'):
                continue
            # update progress
            pDialog.update(0, line1=(STR_GETTING_ITEMS_IN_x % tvshow_label))
            # get everything inside tvshow path
            tvshow_path = ditem['file']
            results = json.loads(xbmc.executeJSONRPC(
                '{"jsonrpc": "2.0", "method": "Files.GetDirectory", \
                "params": {"directory":"%s"}, "id": 1}' % tvshow_path))
            # skip if results don't load
            if not (results.has_key('result') and results["result"].has_key('files')):
                continue
            show_items = results["result"]["files"]
            # get all items to stage in show
            for shitem in show_items:
                # get label and path
                label = shitem['label']
                path = shitem['file']
                # update progress
                pDialog.update(0, line2=label)
                # check for duplicate paths and blocked items
                if dbh.path_exists(path) or dbh.check_blocked(label, 'episode'):
                    continue
                dbh.add_content_item(path, label, content_type, tvshow_label)
                items_to_stage += 1
                pDialog.update(0, line2=' ')
            pDialog.update(0, line1=' ')
        pDialog.close()
        notification(STR_i_EPISODES_STAGED % items_to_stage)
