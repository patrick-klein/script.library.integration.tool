# /usr/bin/python
# -*- coding: utf-8 -*-
'''
Contains various constants and utility functions used thoughout the addon
'''
# TODO: Consider breaking up into more files (or Python package)
import re
import sys

from os import mkdir, name as osname
from os.path import expanduser, join, dirname, isdir, isfile

import simplejson as json

import xbmc # pylint: disable=import-error
import xbmcaddon # pylint: disable=import-error
import xbmcvfs  # pylint: disable=import-error
import xbmcgui

# Get file system tools depending on platform
if osname == 'posix':
    import resources.lib.unix as fs
else:
    import resources.lib.universal as fs

# Get settings
ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_NAME = ADDON.getAddonInfo('name')
ADDON_PATH = ADDON.getAddonInfo('path')
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
    MANAGED_FOLDER = xbmcvfs.translatePath('special://userdata/addon_data/{}/'.format(ADDON_ID))
if USING_CUSTOM_METADATA_FOLDER:
    METADATA_FOLDER = ADDON.getSetting('metadata_folder')
else:
    METADATA_FOLDER = join(MANAGED_FOLDER, 'Metadata')

# Enum values in settings
NEVER = '0'
ALWAYS = '1'
WITH_EPID = '1'
WITH_METADATA = '2'

# Define other constants
DEFAULT_LOG_LEVEL = xbmc.LOGNOTICE if IN_DEVELOPMENT else xbmc.LOGDEBUG
DATABASE_FILE = join(MANAGED_FOLDER, 'managed.db')
# TODO: Use combined list on all platforms.  Would need to be combined with version check
# to re-add all managed items
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

if osname == 'nt':
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
    if not (MANAGED_FOLDER and isdir(MANAGED_FOLDER)):
        # TODO: Open prompt to just set managed folder from here
        STR_CHOOSE_FOLDER = getlocalizedstring(32123)
        notification(STR_CHOOSE_FOLDER)
        log_msg('No managed folder "{}"'.format(MANAGED_FOLDER), xbmc.LOGERROR)
        sys.exit()

def check_subfolders():
    ''' Checks the subfolders in the Managed and Metadata folders '''
    # Create subfolders if they don't exist
    subfolders = [
        join(MANAGED_FOLDER, 'ManagedMovies'),
        join(MANAGED_FOLDER, 'ManagedTV')
    ] + ([] if USING_CUSTOM_METADATA_FOLDER else [join(MANAGED_FOLDER, 'Metadata')]) + [
        join(METADATA_FOLDER, 'Movies'),
        join(METADATA_FOLDER, 'TV')
    ]
    created_folders = False
    for folder in subfolders:
        if not isdir(folder):
            log_msg('Creating subfolder {}'.format(folder), loglevel=xbmc.LOGNOTICE)
            fs.mkdir(folder)
            created_folders |= True
    if created_folders:
        STR_SUBFOLDERS_CREATED = getlocalizedstring(32127)
        notification(STR_SUBFOLDERS_CREATED)
        # TODO: Add video sources here
        sys.exit()

def check_version_file():
    ''' Checks the version file and runs version-specific update actions '''
    # Check version file
    version_file_path = xbmcvfs.translatePath(
        'special://userdata/addon_data/{}/.version'.format(ADDON_ID)
    )
    if isfile(version_file_path):
        with open(version_file_path, 'r') as version_file:
            version = Version(version_file.read())
    else:
        # TODO: Use the following after updating to v0.5.0
        # with open(version_file_path, 'w') as version_file:
        #     version_file.write(ADDON_VERSION)
        # version = Version(ADDON_VERSION)
        version = Version('0.3.2')
    if version != ADDON_VERSION:
        STR_UPDATING = getlocalizedstring(32133)
        STR_UPDATED = getlocalizedstring(32134)
        notification(STR_UPDATING)
        if version < '0.3.0':
            # Update .pkl files
            import resources.lib.update_pkl as update_pkl
            update_pkl.main()
        if version < '0.4.0':
            # Maintain previous settings if managed folder is already set
            if ADDON.getSetting('managed_folder'):
                ADDON.setSetting('custom_managed_folder', 'true')
        # Create addons dir if not exist
        mkdir(dirname(version_file_path))
        # Update version file
        with open(version_file_path, 'w+') as version_file:
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
        return func(*args, **kwargs)
    return wrapper

def log_msg(msg, loglevel=DEFAULT_LOG_LEVEL):
    ''' Log message with addon name and version to kodi log '''
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
                arg_list.append("'{0}'".format(arg))
            for key, val in kwargs.items():
                arg_list.append(
                    '{0}={1}'.format(key, "'{0}'".format(val)))
            arg_str = '({0})'.format(', '.join(arg_list))
            # Add line breaks and limit output if ret value is iterable
            if isinstance(ret, str):
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

# TODO: NETFLIX find a way to deal with show with Part 1,
# Part 2 and etc, now, any part will be a season,
# maybe a api call with trakt or tvdb to get episode info is a way

# TODO: Giant animes like One Piece is devided in folders with 60 eps,
# and not splited by season, maybe all eps need to be in the Show dir
# directly and follow absolute order, to do this is necessary identify this cases.

# TODO: CHRUNCHROLL create a dialog to selec language or
# use system language to auto select:

def clean_name(title):
    ''' Remove/replace problematic characters/substrings for filenames '''
    # IDEA: Replace in title directly, not just filename

    # TODO: use this function to remove from Show/episode title on,
    # Show title
    # episode number
    # (Legendado)
    # (Leg)
    # (Dub PT)
    # (French Dub)
    # (German Dub)
    # (Portuguese Dub)
    # (English Dub)
    # (Spanish Dub)
    # TODO: Efficient algorithm that removes/replaces in a single
    for key, val in MAPPED_STRINGS:
        title = title.replace(key, val)
    return title

def execute_json_rpc(method, directory):
    ''' Execute a JSON-RPC command with specified method and params (as keyword arguments)
    See https://kodi.wiki/view/JSON-RPC_API/v10 for methods and params '''
    return json.loads(
        xbmc.executeJSONRPC(
            json.dumps({
                'jsonrpc': '2.0',
                "method": method,
                "params": {
                    'directory': directory,
                    'properties': [
                        'duration',
                        'season',
                        'title',
                        'file',
                        'showtitle',
                        'year',
                        'episode',
                    ],
                    },
                'id': 1
            }, ensure_ascii=False) # ensure_ascii ONLY scape charters in python3
        )
    )

def videolibrary(method):
    ''' A dedicated method to performe jsonrpc VideoLibrary.Scan or VideoLibrary.Clean '''
    return xbmc.executeJSONRPC(
        json.dumps({
            'jsonrpc': '2.0',
            "method": 'VideoLibrary.Scan' if method == 'scan' else 'VideoLibrary.Clean',
            'id': 1
        }, ensure_ascii=False)
    )

def re_search(string, strings_to_skip=None):
    ''' Function check if string exist with re '''
    STR_SKIP_STRINGS = [
        'resumo',
        'suggested',
        'extras',
        'trailer',
        r'(?i)\#(?:\d{1,5}\.\d{1,5}|SP)',
    ]

    if strings_to_skip:
        STR_SKIP_STRINGS = strings_to_skip
    return bool(any(re.search(rgx, string, re.I) for rgx in STR_SKIP_STRINGS))

def skip_filter(contets_json):
    ''' Function to check and filter items in a list '''
    # TODO: IDEIA, create a new dialog to sync_all_items_in_directory in context2.py,
    # where user can filter show/movies they whant to sync,
    # imagine a list with 30 shows/movies, but user realy want 5,
    # with this they can select dinamicaly first we ask if user want to filter,
    # if yes, the multselection list will apear
    for item in contets_json:
        if not re_search(item['label']):
            yield item

def list_reorder(contets_json, showtitle, year=False, sync_type=False):
    ''' Return a list of elements reordered by number id '''
    reordered = [''] * len(contets_json)
    years = []
    stored_title = None
    stored_season = None
    for index, item in enumerate(contets_json):
        # TODO: check if logic is real necessary, test is for all languages eficient
        STR_SEASON_CHECK = re_search(
            item['label'], ['season', 'temporada', r'S\d{1,4}']
            )
        if sync_type != 'all_items':
            if sync_type == 'movie' and item['type'] == 'movie':
                pass
            elif (sync_type == 'tvshow' and re_search(item['type'],
                      ['tvshow', 'season', 'episode', 'unknown', 'directory'])):
                pass
            elif sync_type == 'music' and item['type'] == 'music':
                pass
            else:
                continue

        item['number'] = index + 1
        # 1601 é o ano que aparece quando a informação de ano correta não existe
        if item['year'] == 1601:
            if year is not False:
                item['year'] = int(year)
            else:
                del item['year']

        # MOVIES: detect movies in dir
        if item['filetype'] == 'file' and item['type'] == 'movie':
            del item['episode']
            del item['season']
            del item['showtitle']
            if item['label'] == item['title']:
                del item['label']
            try:
                item['movie_title'] = item['title']
                del item['title']
            except KeyError:
                pass
            reordered[item['number'] - 1] = item
        else:
            # CRUNCHYROLL
            if 'crunchyroll' in item['file']:
                # CRUNCHYROLL SHOW DIRECTORY
                if item['filetype'] == 'directory':
                    if (re_search(item['type'], ['tvshow', 'unknown']) and not
                            re_search(item['file'], [
                                r'(status|mode)\=(Continuing|status|Completed|series)'
                            ])):
                        item['type'] = 'tvshow'
                        del item['episode']
                        del item['season']
                        del item['title']
                        reordered[item['number'] - 1] = item
                    # CRUNCHYROLL SEASON DIRECTORY
                    if (item['type'] == 'unknown' and
                            re_search(item['file'], ['season='])):
                        del item['episode']
                        item['type'] = 'season'
                        item['showtitle'] = showtitle
                        if item['season'] == 0:
                            item['season'] = 1
                        try:
                            years.append(item['year'])
                        except KeyError:
                            pass
                        reordered[item['number'] - 1] = item
                elif item['filetype'] == 'file':
                    # CRUNCHYROLL EPISODE FILE
                    if re_search(item['file'], ['episode=']):
                        item['type'] = 'episode'
                        try:
                            years.append(item['year'])
                        except KeyError:
                            pass
                        reordered[item['number'] - 1] = item
            # AMAZON
            if 'amazon' in item['file']:
                if item['filetype'] == 'directory':
                    # AMAZON SHOW DIRECTORY
                    if (re_search(item['type'], ['tvshow']) and
                            item['episode'] == -1 and
                            item['season'] == -1 and
                            STR_SEASON_CHECK is False):
                        item['type'] = 'tvshow'
                        item['showtitle'] = item['label']
                        del item['episode']
                        del item['season']
                        reordered[item['number'] - 1] = item
                    # AMAZON SEASON DIRECTORY
                    if (item['type'] == 'unknown' and
                            item['season'] != -1 and
                            STR_SEASON_CHECK is True):
                        del item['episode']
                        del item['number']
                        item['type'] = 'season'
                        item['showtitle'] = showtitle
                        try:
                            years.append(item['year'])
                        except KeyError:
                            pass
                        reordered[item['season'] - 1] = item
                        # TODO: Bad method to get seasons without 'Season' in label
                    elif (item['filetype'] == 'directory' and
                        item['episode'] == -1 and
                        item['season'] != -1 and
                        STR_SEASON_CHECK is False):
                        del item['episode']
                        del item['number']
                        item['type'] = 'season'
                        item['showtitle'] = showtitle
                        try:
                            years.append(item['year'])
                        except KeyError:
                            pass
                        reordered[item['season'] - 1] = item
                elif item['filetype'] == 'file':
                    # AMAZON EPISODE FILE
                    if (item['episode'] != -1 and
                            item['season'] != -1 and
                            item['type'] == 'episode'):
                        try:
                            years.append(item['year'])
                        except KeyError:
                            pass
                        reordered[item['episode'] - 1] = item
            # DISNEY
            if 'disney' in item['file']:
                # DISNEY SHOW DIRECTORY
                if item['filetype'] == 'directory':
                    if (item['type'] == 'tvshow' and
                            item['season'] == -1 and
                            STR_SEASON_CHECK is False):
                        item['showtitle'] = item['title']
                        item['type'] = 'tvshow'
                        del item['episode']
                        del item['season']
                        reordered[item['number'] - 1] = item
                    # DISNEY SEASON DIRECTORY
                    if (item['type'] == 'unknown' and
                            STR_SEASON_CHECK is True):
                        item['showtitle'] = showtitle
                        del item['episode']
                        item['type'] = 'season'
                        try:
                            years.append(item['year'])
                        except KeyError:
                            pass
                        reordered[item['season'] - 1] = item
                elif item['filetype'] == 'file':
                    # DISNEY EPISODE FILE
                    if (item['type'] == 'episode'):
                        try:
                            years.append(item['year'])
                        except KeyError:
                            pass
                        reordered[item['episode'] - 1] = item
            # NETFLIX
            if 'netflix' in item['file']:
                if item['filetype'] == 'directory':
                    # NETFLIX SHOW DIRECTORY
                    if (re_search(item['type'], ['tvshow']) and not
                            re_search(item['file'], ['season', 'episode'])):
                        del item['episode']
                        del item['season']
                        reordered[item['number'] - 1] = item
                    # NETFLIX SEASON DIRECTORY
                    if (item['type'] == 'unknown' and
                            re_search(item['file'], ['show', 'season']) and not
                            re_search(item['file'], ['episode']) and
                            STR_SEASON_CHECK is True):
                        item['showtitle'] = showtitle
                        item['type'] = 'season'
                        del item['episode']
                        try:
                            years.append(item['year'])
                        except KeyError:
                            pass
                        reordered[item['season'] - 1] = item
                elif item['filetype'] == 'file':
                    # NETFLIX EPISODE FILE
                    if (item['type'] == 'episode' and
                            re_search(item['file'], ['show', 'season', 'episode'])):
                        try:
                            years.append(item['year'])
                        except KeyError:
                            pass
                        if item['episode'] != item['number']:
                            reordered[item['number'] - 1] = item
                        else:
                            reordered[item['episode'] - 1] = item
            # this part of code detect episodes with < 30 in season with 'Next Page'
            # works with CRUNCHYROLL, but can work for all
            if (item['filetype'] == 'file' and
                    item['type'] == 'episode'):
                if stored_season and stored_title is None:
                    stored_title = item['showtitle']
                    stored_season = item['season']
                if (item['season'] == stored_season and
                        item['showtitle'] == stored_title and
                        item['episode'] < 30):
                    item['episode'] = item['number']
                if item['season'] != stored_season:
                    stored_season = item['season']
                if item['showtitle'] != stored_title:
                    stored_title = item['showtitle']
    for item in reordered:
        if not item == "":
            try:
                loweryear = min(years)
                item['year'] = loweryear
            except (KeyError, ValueError):
                pass
            yield item

def load_directory_items(progressdialog, dir_path, recursive=False,
                         allow_directories=False, depth=1, showtitle=False,
                         season=False, year=False, sync_type=False):
    ''' Load items in a directory using the JSON-RPC interface '''
    if RECURSION_LIMIT and depth > RECURSION_LIMIT:
        yield []
    results = execute_json_rpc(
        'Files.GetDirectory',
        directory=dir_path)['result']['files']

    if sync_type == 'filter':
        sync_type = 'all_items'
        results = list(selected_list(results))

    try:
        listofitems = list(list_reorder(
            list(skip_filter(results)
                ), showtitle=showtitle, year=year, sync_type=sync_type))
    except KeyError:
        listofitems = []
    if not allow_directories:
        for item in listofitems:
            if item['filetype'] == 'file':
                yield item
    directories = []
    for index, item in enumerate(listofitems):
        if progressdialog.iscanceled() is True:
            progressdialog.close()
            break
        percent = 100 * index / len(listofitems)
        if item['type'] == 'movie':
            progressdialog.update(int(percent), 'Processando items:\n%s' % item['movie_title'])
            xbmc.sleep(200)
            yield item
        else:
            if season is not False:
                item['season'] = season
            if year is not False:
                item['year'] = year
                # # se for um diretorio ele é adicionado a lista directories
            if (item['filetype'] == 'directory' and
                    item['type'] == 'tvshow' or
                    item['type'] == 'season'):
                showtitle = item['showtitle']
                progressdialog.update(int(percent), 'Coletando itens no diretorio!\n%s' % item['label'])
                xbmc.sleep(200)
                directories.append(item)
                # # se for um epsodio, usa o yield para guardar o item
            if item['type'] == 'episode':
                progressdialog.update(int(percent), 'Processando items:\n%s' % item['label'])
                xbmc.sleep(100)
                item['showtitle'] = showtitle
                yield item
    if recursive and directories:
        for _dir in directories:
            # close the progress bar during JSONRPC process
            try:
                title = _dir['showtitle']
                recursive = True
            except KeyError:
                title = False
            try:
                season = _dir['season']
                recursive = True
            except KeyError:
                season = False
            try:
                year = _dir['year']
                recursive = True
            except KeyError:
                year = False
            new_items = list(load_directory_items(
                progressdialog=progressdialog,
                dir_path=_dir['file'],
                recursive=recursive,
                allow_directories=allow_directories,
                depth=depth + 1,
                showtitle=title,
                season=season,
                year=year,
                sync_type=sync_type
                ))
            for new in new_items:
                yield new

def notification(message, time=3000, icon='ntf_icon.png'):
    ''' Provide a shorthand for xbmc builtin notification with addon name '''
    xbmc.executebuiltin('Notification("{0}", "{1}", "{2}", "{3}")'.format(
        ADDON_NAME,
        message,
        time,
        join(ADDON_PATH, icon)
        ))

def tojs(data, filename):
    ''' Function to create a json file '''
    with open(join(expanduser('~/'), filename) + '.json', 'a+') as f:
        f.write(str(json.dumps(data, indent=4, sort_keys=True)))
        f.close()

def getlocalizedstring(string_id):
    ''' Function to get call getLocalizedString and deal with unicodedecodeerrors '''
    return str(ADDON.getLocalizedString(string_id))

def title_with_color(label, year=None, color='skyblue'):
    ''' Create a string to use in title Dialog().select '''
    # COLORS: https://github.com/xbmc/xbmc/blob/master/system/colors.xml
    # TODO: this function can be better, maybe led generic,
    # now, this func add color and year to movie title,
    # and any of this actions can be splited
    if year:
        return str('[COLOR %s][B]%s (%s)[/B][/COLOR]' % (color, label, year))
    return str('[COLOR %s][B]%s[/B][/COLOR]' % (color, label))
