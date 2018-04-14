#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
This module contains various helper functions used thoughout the addon
'''

import xbmc
import xbmcaddon

addon = xbmcaddon.Addon()
STR_ADDON_NAME = addon.getAddonInfo('name')
STR_ADDON_VER = addon.getAddonInfo('version')
MANAGED_FOLDER = addon.getSetting('managed_folder')

def utf8_encode(s):
    ''' tries to force utf-8 encoding '''
    # attempt to encode input
    try:
        s = s.encode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        s = s.decode('utf-8').encode('utf-8')
    return s

def utf8_decorator(func):
    ''' decorator for calling etf8_encode on all arguments '''
    def wrapper(*orig_args, **orig_kwargs):
        ''' decorator wrapper '''
        new_args = list()
        for arg in orig_args:
            if isinstance(arg, basestring):
                arg = utf8_encode(arg)
            new_args.append(arg)
        new_args = tuple(new_args)
        new_kwargs = dict()
        for k, v in orig_kwargs.iteritems():
            if isinstance(v, basestring):
                v = utf8_encode(v)
            new_kwargs[k] = v
        return func(*new_args, **new_kwargs)
    return wrapper

def clean_name(s):
    ''' this function removes problematic characters/substrings from strings for filenames '''
    #TODO?: replace in title directly, not just filename
    c = {'.': '',
         ':': '',
         '/': '',
         '"': '',
         '$': '',
         ' [cc]': '',
         'é': 'e',
         'Part 1': 'Part One',
         'Part 2': 'Part Two',
         'Part 3': 'Part Three',
         'Part 4': 'Part Four',
         'Part 5': 'Part Five',
         'Part 6': 'Part Six',
        }
    for k, v in c.iteritems():
        s = s.replace(k, v)
    return s

def notification(msg):
    ''' provides shorthand for xbmc builtin notification with addon name '''
    xbmc.executebuiltin('Notification("{0}", "{1}")'.format(STR_ADDON_NAME, msg))

def log_msg(msg, loglevel=xbmc.LOGNOTICE):
    ''' log message with addon name and version to kodi log '''
    if isinstance(msg, unicode):
        msg = msg.encode('utf-8')
    xbmc.log("{0} v{1} --> {2}".format(STR_ADDON_NAME, STR_ADDON_VER, msg), level=loglevel)
