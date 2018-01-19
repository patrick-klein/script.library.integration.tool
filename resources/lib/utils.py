#!/usr/bin/python
# -*- coding: utf-8 -*-

import xbmc
import xbmcaddon

import cPickle as pickle

#managed_folder = '/Volumes/Drobo Media/LibraryTools/'

addon = xbmcaddon.Addon()
str_addon_name = addon.getAddonInfo('name')
str_addon_ver = addon.getAddonInfo('version')
managed_folder = addon.getSetting('managed_folder')

def get_items(name):
    # add to staged list
    filename = managed_folder + name
    try:
        items = pickle.load(open(filename,"rb"))
        #log_msg('Opening file %s' % filename, xbmc.LOGNOTICE)
    except IOError:
        items = []
        #log_msg('File not found. Creating %s' % filename, xbmc.LOGNOTICE)
        pickle.dump(items,open(filename,"wb"))
    return items

def save_items(name, items):
    # save staged items
    filename = managed_folder + name
    pickle.dump(items,open(filename,"wb"))

def append_item(name, item):
    items = get_items(name)
    items.append(item)
    save_items(name, items)

def remove_item(name, item):
    items = get_items(name)
    items.remove(item)
    save_items(name, items)

def clean(s):
    #TODO: test stripping '.', '%'
    #TODO: replace part # in title directly, not just filename
    return s.replace(':','').replace('/','').replace('Part 1', 'Part One').replace('Part 2', 'Part Two')

def localize_blocktype(mediatype):
    if mediatype=='movie':      # Movie
        return addon.getLocalizedString(32102)
    elif mediatype=='tvshow':   # TV Show
        return addon.getLocalizedString(32101)
    elif mediatype=='keyword':  # Keyword
        return addon.getLocalizedString(32113)
    elif mediatype=='episode':  # Episode
        return addon.getLocalizedString(32114)
    else:
        return mediatype

def localize_synctype(mediatype):
    if mediatype=='movie':      # Movies
        return addon.getLocalizedString(32109)
    elif mediatype=='tvshow':   # TV Shows
        return addon.getLocalizedString(32108)
    elif mediatype=='single-movie': # Single Movie
        return addon.getLocalizedString(32116)
    elif mediatype=='single-tvshow':  # Single TV Show
        return addon.getLocalizedString(32115)
    else:
        return mediatype

def log_msg(msg, loglevel=xbmc.LOGDEBUG):
    #TODO: add version number to log string
    '''log message to kodi log'''
    if isinstance(msg, unicode):
        msg = msg.encode('utf-8')
    xbmc.log("{0} v{1} --> {2}".format(str_addon_name, str_addon_ver, msg), level=loglevel)
