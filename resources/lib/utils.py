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
    ''' returns string (re)encoded as utf-8 '''
    try:
        return s.encode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s.decode('utf-8').encode('utf-8')

def utf8_decorator(func):
    ''' decorator for calling utf8_encode on all string arguments '''
    def wrapper(*args, **kwargs):
        ''' function wrapper '''
        new_args = (utf8_encode(x) if isinstance(x, basestring) else x for x in args)
        new_kwargs = {k: utf8_encode(v) if isinstance(v, basestring) else v \
            for k, v in kwargs.iteritems()}
        return func(*new_args, **new_kwargs)
    return wrapper

def log_msg(msg, loglevel=xbmc.LOGNOTICE):
    ''' log message with addon name and version to kodi log '''
    if isinstance(msg, unicode):
        msg = msg.encode('utf-8')
    xbmc.log("{0} v{1} --> {2}".format(STR_ADDON_NAME, STR_ADDON_VER, msg), level=loglevel)

def log_decorator(func):
    ''' decorator for logging function call and return values '''
    def wrapper(*args, **kwargs):
        ''' function wrapper '''
        # call the function and get the return value
        ret = func(*args, **kwargs)
        # define the string for the function call (include class name for methods)
        is_method = hasattr(args[0].__class__, func.__name__)
        if is_method:
            func_str = '{0}.{1}'.format(args[0].__class__.__name__, func.__name__)
        else:
            func_str = '{0}.{1}'.format(func.__module__.replace('resources.lib.', ''), func.__name__)
        # pretty formating for argument string
        arg_list = list()
        for arg in args[1 if is_method else 0:]:
            arg_list.append("'{0}'".format(arg) if isinstance(arg, basestring) else str(arg))
        for k, v in kwargs.iteritems():
            arg_list.append('{0}={1}'\
                .format(k, "'{0}'".format(v) if isinstance(v, basestring) else str(v)))
        arg_str = '({0})'.format(', '.join(arg_list))
        # add line breaks and limit output if ret value is iterable
        try:
            ret_list = ['\n'+str(x) for x in ret[:5]]
            if len(ret) > 5:
                ret_list += ['\n+{0} more items...'.format(len(ret)-5)]
            ret_str = str().join(ret_list)
        except TypeError:
            ret_str = str(ret)
        # log message at default loglevel
        message = '{0}{1}: {2}'.format(func_str, arg_str, ret_str)
        log_msg(message)
        # return ret value from wrapper
        return ret
    return wrapper

def clean_name(s):
    ''' this function removes/replaces problematic characters/substrings from strings for filenames '''
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
