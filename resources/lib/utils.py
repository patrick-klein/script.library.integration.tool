#!/usr/bin/python
# -*- coding: utf-8 -*-

import cPickle as pickle
import xbmc

managed_folder = '/Volumes/Drobo Media/LibraryTools/'

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
    return s.replace(':','').replace('/','').replace('Part 1', 'Part One').replace('Part 2', 'Part Two')

def log_msg(msg, loglevel=xbmc.LOGDEBUG):
    #TODO: add version number to log string
    '''log message to kodi log'''
    if isinstance(msg, unicode):
        msg = msg.encode('utf-8')
    xbmc.log("Library Integration Tool --> %s" % msg, level=loglevel)
