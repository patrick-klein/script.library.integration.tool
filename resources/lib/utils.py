#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
This module contains various helper functions used thoughout the addon
'''
#TODO: 'Notification' shorthand

import cPickle as pickle

import xbmc
import xbmcaddon

addon = xbmcaddon.Addon()
STR_ADDON_NAME = addon.getAddonInfo('name')
STR_ADDON_VER = addon.getAddonInfo('version')
MANAGED_FOLDER = addon.getSetting('managed_folder')

def get_items(name):
    ''' this function returns the items in the specified pickle file '''
    filename = MANAGED_FOLDER + name
    try:
        items = pickle.load(open(filename, "rb"))
        log_msg('Opening file %s' % filename, xbmc.LOGNOTICE)
    except IOError:
        items = []
        log_msg('Creating %s' % filename)
        pickle.dump(items, open(filename, "wb"))
    return items

def save_items(name, items):
    ''' this function saves the items into the specified pickle file '''
    filename = MANAGED_FOLDER + name
    pickle.dump(items, open(filename, "wb"))

def append_item(name, item):
    ''' this function opens the specifies pickle file, appends the item, then saves it '''
    items = get_items(name)
    items.append(item)
    save_items(name, items)

def remove_item(name, item):
    ''' this function opens the specifies pickle file, removes the item, then saves it '''
    items = get_items(name)
    items.remove(item)
    save_items(name, items)

def clean_name(s):
    ''' this function removes problematic characters/substrings from strings for filenames '''
    #?TODO: replace in title directly, not just filename
    s = s.replace('.', '')
    s = s.replace(':', '')
    s = s.replace('/', '')
    s = s.replace('Part 1', 'Part One')
    s = s.replace('Part 2', 'Part Two')
    s = s.replace(' [cc]', '')
    return s

def notification(msg):
    xbmc.executebuiltin('Notification("{0}", "{1}")'.format(STR_ADDON_NAME, msg))

def log_msg(msg, loglevel=xbmc.LOGDEBUG):
    ''' log message with addon name and version to kodi log '''
    if isinstance(msg, unicode):
        msg = msg.encode('utf-8')
    xbmc.log("{0} v{1} --> {2}".format(STR_ADDON_NAME, STR_ADDON_VER, msg), level=loglevel)
