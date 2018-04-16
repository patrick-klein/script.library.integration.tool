#!/usr/bin/python
# -*- coding: utf-8 -*-
''' This is a post-update script that converts the .pkl files to a SQLite database '''

import os
import cPickle as pickle

import xbmcaddon
import xbmcgui

from utils import log_decorator
from database_handler import DB_Handler

addon = xbmcaddon.Addon()
STR_ADDON_NAME = addon.getAddonInfo('name')
MANAGED_FOLDER = addon.getSetting('managed_folder')

@log_decorator
def update_managed():
    ''' Converts managed.pkl items to SQLite entries '''
    managed_file = os.path.join(MANAGED_FOLDER, 'managed.pkl')
    if os.path.exists(managed_file):
        dbh = DB_Handler()
        items = pickle.load(open(managed_file, 'rb'))
        for item in items:
            if item.get_mediatype() == 'movie':
                dbh.add_content_item(item.get_path(), item.get_title(), 'movie')
            elif item.get_mediatype() == 'tvshow':
                dbh.add_content_item(item.get_path(), item.get_title(), 'tvshow', \
                    item.get_show_title())
            dbh.update_content_status(item.get_path(), 'managed')
        os.remove(managed_file)

@log_decorator
def update_staged():
    ''' Converts staged.pkl items to SQLite entries '''
    staged_file = os.path.join(MANAGED_FOLDER, 'staged.pkl')
    if os.path.exists(staged_file):
        dbh = DB_Handler()
        items = pickle.load(open(staged_file, 'rb'))
        for item in items:
            if item.get_mediatype() == 'movie':
                dbh.add_content_item(item.get_path(), item.get_title(), 'movie')
            elif item.get_mediatype() == 'tvshow':
                dbh.add_content_item(item.get_path(), item.get_title(), 'tvshow', \
                    item.get_show_title())
        os.remove(staged_file)

@log_decorator
def update_synced():
    ''' Converts managed.pkl items to SQLite entries '''
    synced_file = os.path.join(MANAGED_FOLDER, 'synced.pkl')
    if os.path.exists(synced_file):
        dbh = DB_Handler()
        items = pickle.load(open(synced_file, 'rb'))
        for item in items:
            dbh.add_synced_dir('NULL', item['dir'], item['mediatype'])
        os.remove(synced_file)

@log_decorator
def update_blocked():
    ''' Converts blocked.pkl items to SQLite entries '''
    blocked_file = os.path.join(MANAGED_FOLDER, 'blocked.pkl')
    if os.path.exists(blocked_file):
        dbh = DB_Handler()
        items = pickle.load(open(blocked_file, 'rb'))
        for item in items:
            if item['type'] != 'keyword':
                dbh.add_blocked_item(item['label'], item['type'])
        os.remove(blocked_file)

@log_decorator
def main():
    ''' main entrypoint for module
    updates log and progress, and calls all other functions '''

    STR_UPDATING = addon.getLocalizedString(32133)
    pDialog = xbmcgui.DialogProgress()
    pDialog.create(STR_ADDON_NAME, STR_UPDATING)

    pDialog.update(0, line2='managed.pkl')
    update_managed()

    pDialog.update(25, line2='staged.pkl')
    update_staged()

    pDialog.update(50, line2='synced.pkl')
    update_synced()

    pDialog.update(75, line2='blocked.pkl')
    update_blocked()

    pDialog.close()
