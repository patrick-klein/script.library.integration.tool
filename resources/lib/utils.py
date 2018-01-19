#!/usr/bin/python
# -*- coding: utf-8 -*-

import xbmc
import xbmcaddon

import cPickle as pickle

managed_folder = '/Volumes/Drobo Media/LibraryTools/'
addon = xbmcaddon.Addon()
str_addon_name = addon.getAddonInfo('name')
str_addon_ver = addon.getAddonInfo('version')

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

def localize_mediatype(mediatype):
    #TODO: string file
    if mediatype=='movie':
        return addon.getLocalizedString(32102)
    elif mediatype=='show':
        return addon.getLocalizedString(32101)
    elif mediatype=='keyword':
        return addon.getLocalizedString(32113)
    elif mediatype=='episode':
        return addon.getLocalizedString(32114)

def log_msg(msg, loglevel=xbmc.LOGDEBUG):
    #TODO: add version number to log string
    '''log message to kodi log'''
    if isinstance(msg, unicode):
        msg = msg.encode('utf-8')
    xbmc.log("{0} ({1}) --> {1}".format(str_addon_name, str_addon_ver, msg), level=loglevel)
