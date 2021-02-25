#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Script that converts old-style .pkl files to a SQLite database
'''

import os

import cPickle as pickle
import xbmc # pylint: disable=import-error

import resources.lib.utils as utils
from resources.lib.database_handler import DatabaseHandler


@utils.logged_function
def update_managed():
    ''' Convert managed.pkl items to SQLite entries '''
    managed_file = os.path.join(utils.MANAGED_FOLDER, 'managed.pkl')
    if os.path.exists(managed_file):
        dbh = DatabaseHandler()
        items = pickle.load(open(managed_file, 'rb'))
        for item in items:
            if item.mediatype == 'movie':
                dbh.add_content_item(item.path, item.title, 'movie')
            elif item.mediatype == 'tvshow':
                dbh.add_content_item(
                    item.path,
                    item.title,
                    'tvshow',
                    item.show_title
                )
            dbh.update_content(item.path, status='managed')
        os.remove(managed_file)


@utils.logged_function
def update_staged():
    ''' Convert staged.pkl items to SQLite entries '''
    staged_file = os.path.join(utils.MANAGED_FOLDER, 'staged.pkl')
    if os.path.exists(staged_file):
        dbh = DatabaseHandler()
        items = pickle.load(open(staged_file, 'rb'))
        for item in items:
            if item.mediatype == 'movie':
                dbh.add_content_item(item.path, item.title, 'movie')
            elif item.mediatype == 'tvshow':
                dbh.add_content_item(item.path, item.title, 'tvshow', \
                    item.show_title)
        os.remove(staged_file)


@utils.logged_function
def update_synced():
    ''' Convert managed.pkl items to SQLite entries '''
    #TODO: Actually load paths and try to get new label
    synced_file = os.path.join(utils.MANAGED_FOLDER, 'synced.pkl')
    if os.path.exists(synced_file):
        dbh = DatabaseHandler()
        items = pickle.load(open(synced_file, 'rb'))
        for item in items:
            dbh.add_synced_dir('NULL', item['dir'], item['mediatype'])
        os.remove(synced_file)


@utils.logged_function
def update_blocked():
    ''' Convert blocked.pkl items to SQLite entries '''
    blocked_file = os.path.join(utils.MANAGED_FOLDER, 'blocked.pkl')
    if os.path.exists(blocked_file):
        dbh = DatabaseHandler()
        items = pickle.load(open(blocked_file, 'rb'))
        for item in items:
            if item['type'] != 'keyword':
                dbh.add_blocked_item(item['label'], item['type'])
        os.remove(blocked_file)


@utils.logged_function
def main():
    ''' Main entrypoint for module.
    Update log and call other functions to update files '''
    utils.log_msg('Updating pickle files...', xbmc.LOGNOTICE)
    update_managed()
    update_staged()
    update_synced()
    update_blocked()
    utils.log_msg('Pickle files updated.', xbmc.LOGNOTICE)
