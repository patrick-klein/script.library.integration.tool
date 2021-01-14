#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Contains various constants and utility functions used thoughout the addon
'''

# TODO: Consider breaking up into more files (or Python package)

import os
import sys

import simplejson as json
import xbmc
import xbmcaddon

# Get file system tools depending on platform
if os.name == 'posix':
    import resources.lib.unix as fs
else:
    import resources.lib.universal as fs

# Get settings
ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_NAME = ADDON.getAddonInfo('name')
ADDON_VERSION = ADDON.getAddonInfo('version')
AUTO_ADD_MOVIES = ADDON.getSetting('auto_add_movies')
AUTO_ADD_TVSHOWS = ADDON.getSetting('auto_add_tvshows')
IN_DEVELOPMENT = ADDON.getSetting('in_development') == 'true'
RECURSION_LIMIT = int(ADDON.getSetting('recursion_limit'))
USE_SHOW_ARTWORK = ADDON.getSetting('use_show_artwork') == 'true'
USING_CUSTOM_MANAGED_FOLDER = ADDON.getSetting('custom_managed_folder') == 'true'
USING_CUSTOM_METADATA_FOLDER = ADDON.getSetting('custom_metadata_folder') == 'true'
if USING_CUSTOM_MANAGED_FOLDER:
    MANAGED_FOLDER = ADDON.getSetting('managed_folder')
else:
    MANAGED_FOLDER = xbmc.translatePath('special://userdata/addon_data/{}/'.format(ADDON_ID))
if USING_CUSTOM_METADATA_FOLDER:
    METADATA_FOLDER = ADDON.getSetting('metadata_folder')
else:
    METADATA_FOLDER = os.path.join(MANAGED_FOLDER, 'Metadata')

# Enum values in settings
NEVER = '0'
ALWAYS = '1'
WITH_EPID = '1'
WITH_METADATA = '2'

# Define other constants
DEFAULT_LOG_LEVEL = xbmc.LOGNOTICE if IN_DEVELOPMENT else xbmc.LOGDEBUG
DATABASE_FILE = os.path.join(MANAGED_FOLDER, 'managed.db')
# TODO: Use combined list on all platforms.  Would need to be combined with version check
#       to re-add all managed items
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


class Version(object):
    ''' Class that implements comparison operators for version numbers '''

    def __init__(self, version_number):
        self.version_number = version_number

    def __eq__(self, other):
        if isinstance(other, Version):
            return self.version_number == other.version_number
        return self.version_number == other

    def __lt__(self, other):
        if isinstance(other, Version):
            other_version = other.version_number
        else:
            other_version = other
        for this, that in zip(self.version_number.split('.'), other_version.split('.')):
            if int(this) < int(that):
                return True
            elif int(this) > int(that):
                return False
        return False

    def __ne__(self, other):
        return not self == other

    def __gt__(self, other):
        return not (self < other or self == other)

    def __le__(self, other):
        return self < other or self == other

    def __ge__(self, other):
        return self > other or self == other


def check_managed_folder():
    ''' Checks if the managed folder is configured '''
    # Display an error is user hasn't configured managed folder yet
    if not (MANAGED_FOLDER and os.path.isdir(MANAGED_FOLDER)):
        # TODO: Open prompt to just set managed folder from here
        STR_CHOOSE_FOLDER = ADDON.getLocalizedString(32123)
        notification(STR_CHOOSE_FOLDER)
        log_msg('No managed folder "{}"'.format(MANAGED_FOLDER), xbmc.LOGERROR)
        sys.exit()


def check_subfolders():
    ''' Checks the subfolders in the Managed and Metadata folders '''
    # Create subfolders if they don't exist
    subfolders = [
        os.path.join(MANAGED_FOLDER, 'ManagedMovies'),
        os.path.join(MANAGED_FOLDER, 'ManagedTV')
    ] + ([] if USING_CUSTOM_METADATA_FOLDER else [os.path.join(MANAGED_FOLDER, 'Metadata')]) + [
        os.path.join(METADATA_FOLDER, 'Movies'),
        os.path.join(METADATA_FOLDER, 'TV')
    ]
    created_folders = False
    for folder in subfolders:
        if not os.path.isdir(folder):
            log_msg('Creating subfolder {}'.format(folder), loglevel=xbmc.LOGNOTICE)
            fs.mkdir(folder)
            created_folders |= True
    if created_folders:
        STR_SUBFOLDERS_CREATED = ADDON.getLocalizedString(32127)
        notification(STR_SUBFOLDERS_CREATED)
        # TODO: Add video sources here
        sys.exit()


def check_version_file():
    ''' Checks the version file and runs version-specific update actions '''
    # Check version file
    version_file_path = xbmc.translatePath(
        'special://userdata/addon_data/{}/.version'.format(ADDON_ID)
    )
    if os.path.isfile(version_file_path):
        with open(version_file_path, 'r') as version_file:
            version = Version(version_file.read())
    else:
        # TODO: Use the following after updating to v0.5.0
        # with open(version_file_path, 'w') as version_file:
        #     version_file.write(ADDON_VERSION)
        # version = Version(ADDON_VERSION)
        version = Version('0.3.2')
    if version != ADDON_VERSION:
        STR_UPDATING = ADDON.getLocalizedString(32133)
        STR_UPDATED = ADDON.getLocalizedString(32134)
        notification(STR_UPDATING)
        if version < '0.3.0':
            # Update .pkl files
            import resources.lib.update_pkl as update_pkl
            update_pkl.main()
        if version < '0.4.0':
            # Maintain previous settings if managed folder is already set
            if ADDON.getSetting('managed_folder'):
                ADDON.setSetting('custom_managed_folder', 'true')
        # Update version file
        with open(version_file_path, 'w') as version_file:
            version_file.write(ADDON_VERSION)
        notification(STR_UPDATED)
        sys.exit()


def entrypoint(func):
    ''' Decorator to perform actions required for entrypoints '''

    def wrapper(*args, **kwargs):
        ''' function wrapper '''
        check_version_file()
        check_managed_folder()
        check_subfolders()
        return func(*args, **kwargs)

    return wrapper


def utf8_args(func):
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


def log_msg(msg, loglevel=DEFAULT_LOG_LEVEL):
    ''' Log message with addon name and version to kodi log '''
    if isinstance(msg, unicode):
        msg = msg.encode('utf-8')
    xbmc.log("{0} v{1} --> {2}".format(ADDON_NAME, ADDON_VERSION, msg), level=loglevel)


def logged_function(func):
    ''' Decorator for logging function call and return values (at default log level) '''

    # TODO: option to have "pre-" and "post-" logging
    def wrapper(*args, **kwargs):
        ''' function wrapper '''
        # Call the function and get the return value
        ret = func(*args, **kwargs)
        # Only log if IN_DEVELOPMENT is set
        if IN_DEVELOPMENT:
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
    ''' Remove/replace problematic characters/substrings for filenames '''
    # IDEA: Replace in title directly, not just filename
    # TODO: Efficient algorithm that removes/replaces in a single pass
    for key, val in MAPPED_STRINGS:
        name = name.replace(key, val)
    return name


@logged_function
def execute_json_rpc(method, **params):
    ''' Execute a JSON-RPC command with specified method and params (as keyword arguments)
    See https://kodi.wiki/view/JSON-RPC_API/v8#Methods for methods and params '''
    return json.loads(
        xbmc.executeJSONRPC(
            json.dumps({
                'jsonrpc': '2.0',
                "method": method,
                "params": params,
                'id': 1
            })
        )
    )

def index_items(listofitems, limits):
    # "season": "Season 1",
    # "showtitle": "Pose",
    # "type": "episode"

    # "limits": {
    #     "end": 6,
    #     "start": 0,
    #     "total": 6
    # }        

    numbereditems = []

    start = limits['start']
    end = limits['end']

    for num, item in zip(range(start, end), listofitems):
        item['number'] = start + 1
        numbereditems.append(item)
        start += 1
    return numbereditems

@logged_function
def load_directory_items(dir_path, recursive=False, allow_directories=False, depth=1, showtitle=False, season=False):
    ''' Load items in a directory using the JSON-RPC interface '''
    if RECURSION_LIMIT and depth > RECURSION_LIMIT:
        return []
    # Send command to load results
    results = execute_json_rpc('Files.GetDirectory', directory=dir_path)
    # save limits to use in future
    limits = results['result']['limits']
    # all itens, movies and epsodes will be stored in this list
    files = []
    # Return nothing if results do not load
    if not (results.has_key('result') and results['result'].has_key('files')):
        return []

    if not allow_directories:
        files = [x for x in results if x['filetype'] == 'file']
    
    try:
        # try to get ['result']['files'] and index_items() 
        listofitems = index_items(results['result']['files'], limits)
    except KeyError:
        # if ['result']['files'] not exist, return a list with nothing 
        # ATENTION: it need be tested to check if don't create errors in future
        listofitems = []

    # in first moment, all show directories wiil be stored here
    directories = []
    for item in listofitems:
        # if show title is not False, set item['showtitle'] as showtitle passed from func argumet
        if showtitle != False:
            item['showtitle'] = showtitle
            pass

        # if show season is not False, set item['season'] as showtitle passed from func argumet
        if season != False:
            item['season'] = season
            pass
        # this part determine what will be made with all items 
        if 'amazon' in item['file'] and item['filetype'] == 'directory' and not 'Season' in item['label'] and not item['type'] == 'episode':
            # amazon animes came two possible informations, tvshow or unknown
            item['type'] = 'tvshow'
            item['showtitle'] = item['label']
            del item['label']
            # if is a show item is added to directories list to use in future
            directories.append(item)
        if item['filetype'] == 'file' and item['type'] == 'episode':
            # if is a epsode the label is changed to ['eptitle'] in dict
            item['eptitle'] = item['label']
            del item['label']
            files.append(item)
        elif item['filetype'] == 'file' and item['type'] == 'movie':
            # if is a movie is added to directly to list
            item['movietitle'] = item['label']
            del item['label']
            files.append(item)
        elif item['filetype'] == 'directory' and item['type'] == 'tvshow':
            # if is a epsode the label is changed to ['eptitle'] in dict
            try:
                item['showtitle'] = item['label']
                del item['label']
            except KeyError as e:
                pass
            # if is a show item is added to directories list to use in future
            directories.append(item)
        elif item['filetype'] == 'directory' and item['type'] == 'unknown' and 'Season' in item['label']:
            # kodi return seasons as a 'directory' and type is unknown
            # ATENTION: it need to be more tested, but now, i don't seed any othe item with this structure
            item['season'] = item['number']
            del item['label']            
            # if is a show item is added to directories list to use in future
            directories.append(item)

    if recursive:
        # load all items recursive based in all dirs
        for _dir in directories:
            try:
                # if _dir has the key showtitle will be defined as title
                title = _dir['showtitle']
                # and the loop will continue
                recursive = True
            except Exception as e:
                title = False
                pass

            try:
                # if _dir has the key season will be defined as season
                season = _dir['season']
                # and the loop will continue
                recursive = True
            except Exception as e:
                season = False
                pass

            # here, the items will be loaded from directories and stored in new_items
            # if title and season is present, we will pass them to use in future
            new_items = load_directory_items(
                _dir['file'],
                recursive=recursive,
                allow_directories=allow_directories,
                depth=depth + 1,
                showtitle=title,
                season=season
            )
            # store all new_items in files
            for new in new_items:
                files.append(new)
                pass
    return files

@logged_function
def notification(message):
    ''' Provide a shorthand for xbmc builtin notification with addon name '''
    xbmc.executebuiltin('Notification("{0}", "{1}")'.format(ADDON_NAME, message))
