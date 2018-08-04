#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
This module contains various helper functions used thoughout the addon
'''
#TODO: create a global IN_DEVELOPMENT variable to enable/disable various features

import os
import sys

import simplejson as json
import xbmc
import xbmcaddon

ADDON = xbmcaddon.Addon()
STR_ADDON_NAME = ADDON.getAddonInfo('name')
STR_ADDON_VER = ADDON.getAddonInfo('version')
MANAGED_FOLDER = ADDON.getSetting('managed_folder')
RECURSION_LIMIT = ADDON.getSetting('recursion_limit')

MAPPED_STRINGS = [
    ('.', ''),
    (':', ''),
    ('/', ''),
    ('"', ''),
    ('$', ''),
    ('é', 'e'),
    (' [cc]', ''),
    ('Part 1', 'Part One'),
    ('Part 2', 'Part Two'),
    ('Part 3', 'Part Three'),
    ('Part 4', 'Part Four'),
    ('Part 5', 'Part Five'),
    ('Part 6', 'Part Six'),
]
if os.name == 'nt':
    MAPPED_STRINGS += [
        ('?', ''),
        ('<', ''),
        ('>', ''),
        ('\\', ''),
        ('*', ''),
        ('|', ''),
        #('+', ''), (',', ''), (';', ''), ('=', ''), ('[', ''), (']', ''),
    ]


def entrypoint(func):
    ''' Decorator to perform actions required for entrypoints '''

    def wrapper(*args, **kwargs):
        ''' function wrapper '''
        # Display an error is user hasn't configured managed folder yet
        if not (MANAGED_FOLDER and os.path.isdir(MANAGED_FOLDER)):
            #TODO: open prompt to just set managed folder from here
            STR_CHOOSE_FOLDER = ADDON.getLocalizedString(32123)
            notification(STR_CHOOSE_FOLDER)
            log_msg('No managed folder!', xbmc.LOGERROR)
            sys.exit()
        # Update .pkl files if present
        if any(x.endswith('.pkl') for x in os.listdir(MANAGED_FOLDER)):
            import resources.lib.update_pkl as update_pkl
            update_pkl.main()
        return func(*args, **kwargs)

    return wrapper


def utf8_decorator(func):
    ''' Decorator for encoding utf8 on all unicode arguments '''

    def wrapper(*args, **kwargs):
        ''' function wrapper '''
        new_args = (x.encode('utf-8') if isinstance(x, unicode) else x for x in args)
        new_kwargs = {
            k: v.encode('utf-8') if isinstance(v, unicode) else v
            for k, v in kwargs.iteritems()
        }
        return func(*new_args, **new_kwargs)

    return wrapper


def log_msg(msg, loglevel=xbmc.LOGDEBUG):
    ''' Log message with addon name and version to kodi log '''
    if isinstance(msg, unicode):
        msg = msg.encode('utf-8')
    xbmc.log("{0} v{1} --> {2}".format(STR_ADDON_NAME, STR_ADDON_VER, msg), level=loglevel)


def log_decorator(func):
    ''' Decorator for logging function call and return values '''

    #TODO: option to have "pre-" and "post-" logging
    #TODO: accept log level as input, with a special "LOGDEV" that only logs if IN_DEVELOPMENT
    def wrapper(*args, **kwargs):
        ''' function wrapper '''
        # Call the function and get the return value
        ret = func(*args, **kwargs)
        # Define the string for the function call (include class name for methods)
        is_method = args and hasattr(args[0].__class__, func.__name__)
        parent = args[0].__class__.__name__ if is_method else func.__module__.replace(
            'resources.lib.', ''
        )
        func_str = '{0}.{1}'.format(parent, func.__name__)
        # Pretty formating for argument string
        arg_list = list()
        for arg in args[1 if is_method else 0:]:
            arg_list.append("'{0}'".format(arg) if isinstance(arg, basestring) else str(arg))
        for key, val in kwargs.iteritems():
            arg_list.append(
                '{0}={1}'
                .format(key, "'{0}'".format(val) if isinstance(val, basestring) else str(val))
            )
        arg_str = '({0})'.format(', '.join(arg_list))
        # Add line breaks and limit output if ret value is iterable
        if isinstance(ret, basestring):
            ret_str = "'{0}'".format(ret)
        else:
            try:
                ret_list = ['\n' + str(x) for x in ret[:5]]
                if len(ret) > 5:
                    ret_list += ['\n+{0} more items...'.format(len(ret) - 5)]
                ret_str = str().join(ret_list)
            except TypeError:
                ret_str = str(ret)
        # Log message at default loglevel
        message = '{0}{1}: {2}'.format(func_str, arg_str, ret_str)
        log_msg(message)
        # Return ret value from wrapper
        return ret

    return wrapper


def clean_name(name):
    ''' Removes/replaces problematic characters/substrings for filenames '''
    #IDEA: replace in title directly, not just filename
    #TODO: efficient algorithm that removes/replaces in a single pass
    for key, val in MAPPED_STRINGS:
        name = name.replace(key, val)
    return name


@log_decorator
def load_directory_items(dir_path, recursive=False, allow_directories=False, depth=1):
    ''' Load items in a directory using the JSON-RPC interface '''
    if RECURSION_LIMIT and depth > RECURSION_LIMIT:
        return []
    # Send command to load results
    results = json.loads(
        xbmc.executeJSONRPC(
            '''{"jsonrpc": "2.0", "method": "Files.GetDirectory",
            "params": {"directory":"%s"}, "id": 1}''' % dir_path
        )
    )
    # Return nothing if results do not load
    if not (results.has_key('result') and results['result'].has_key('files')):
        return []
    # Get files from results
    items = results['result']['files']
    if not allow_directories:
        files = [x for x in items if x['filetype'] == 'file']
    if recursive:
        # Load subdirectories and add items
        directories = [x for x in items if x['filetype'] == 'directory']
        new_items = []
        for directory in directories:
            new_items += load_directory_items(
                directory['file'],
                recursive=recursive,
                allow_directories=allow_directories,
                depth=depth + 1
            )
        if allow_directories:
            items += new_items
        else:
            files += new_items
    return items if allow_directories else files


@log_decorator
def notification(msg):
    ''' Provides shorthand for xbmc builtin notification with addon name '''
    xbmc.executebuiltin('Notification("{0}", "{1}")'.format(STR_ADDON_NAME, msg))
