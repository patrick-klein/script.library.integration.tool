# /usr/bin/python
# -*- coding: utf-8 -*-

"""Contains various constants and utility functions used thoughout the addon."""

import re
import simplejson as json

from os import name as osname

from os.path import join
from os.path import exists
from os.path import expanduser

import xbmc  # pylint: disable=import-error
import xbmcgui  # pylint: disable=import-error
import xbmcvfs  # pylint: disable=import-error

from resources import ADDON
from resources import ADDON_ID
from resources import ADDON_NAME
from resources import ADDON_PATH
from resources import RECURSION_LIMIT
from resources import USING_CUSTOM_MANAGED_FOLDER
from resources import USING_CUSTOM_METADATA_FOLDER

from resources.lib.log import log_msg
from resources.lib.filesystem import mkdir
from resources.lib.version import check_version_file


if USING_CUSTOM_MANAGED_FOLDER:
    MANAGED_FOLDER = ADDON.getSetting('managed_folder')
else:
    MANAGED_FOLDER = xbmcvfs.translatePath(
        'special://userdata/addon_data/{}/'.format(ADDON_ID))

if USING_CUSTOM_METADATA_FOLDER:
    METADATA_FOLDER = ADDON.getSetting('metadata_folder')
else:
    METADATA_FOLDER = join(MANAGED_FOLDER, 'Metadata')


def check_managed_folder():
    """Check if the managed folder is configured."""
    if not exists(MANAGED_FOLDER):
        STR_CHOOSE_FOLDER = 'Created managed folder "{}"'.format(
            MANAGED_FOLDER)
        mkdir(MANAGED_FOLDER)
        log_msg(STR_CHOOSE_FOLDER, xbmc.LOGERROR)


def check_subfolders():
    """Check the subfolders in the Managed and Metadata folders."""
    # Create subfolders if they don't exist
    subfolders = {
        'ManagedMovies': MANAGED_FOLDER,
        'ManagedTV': MANAGED_FOLDER,
        'Movies': METADATA_FOLDER,
        'TV': METADATA_FOLDER,
    }

    if not USING_CUSTOM_METADATA_FOLDER:
        subfolders['Metadata'] = MANAGED_FOLDER

    created_folders = False
    for basepath, diretory in subfolders.items():
        dest_dir = join(diretory, basepath)
        if not exists(dest_dir):
            log_msg('Creating subfolder {}'.format(
                dest_dir), loglevel=xbmc.LOGINFO)
            mkdir(dest_dir)
            created_folders = True

    if created_folders:
        STR_SUBFOLDERS_CREATED = getlocalizedstring(32127)
        notification(STR_SUBFOLDERS_CREATED)
        # TODO: Add video sources here
        xbmc.sleep(1)


def entrypoint(func):
    """Decorator to perform actions required for entrypoints."""
    def wrapper(*args, **kwargs):
        """function wrapper."""
        check_version_file()
        check_managed_folder()
        check_subfolders()
        return func(*args, **kwargs)
    return wrapper


def execute_json_rpc(method, _path):
    """
    Execute a JSON-RPC command with specified method and params (as keyword arguments).

    See https://kodi.wiki/view/JSON-RPC_API/v10 for methods and params.
    """
    return json.loads(
        xbmc.executeJSONRPC(
            json.dumps({
                'jsonrpc': '2.0',
                "method": method,
                "params": {
                    'directory': _path,
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
            }, ensure_ascii=False)  # ensure_ascii ONLY scape charters in python3
        )
    )


def videolibrary(method):
    """A dedicated method to performe jsonrpc VideoLibrary.Scan or VideoLibrary."""
    return xbmc.executeJSONRPC(
        json.dumps({
            'jsonrpc': '2.0',
            "method": 'VideoLibrary.Scan' if method == 'scan' else 'VideoLibrary.Clean',
            'id': 1
        }, ensure_ascii=False)
    )


SKIP_STRINGS = [
    'resumo',
    'suggested',
    'extras',
    'trailer',
    r'(?i)\#(?:\d{1,5}\.\d{1,5}|SP)',
]


def re_search(string, tosearch=None):
    """Function check if string exist with re."""
    return bool(any(re.search(rgx, string, re.I) for rgx in tosearch))


def skip_filter(contents_json, _key, toskip):
    """Function to iterate jsons in a list and filter by key with re."""
    try:
        for item in contents_json:
            if not bool(any(re.search(rgx, item[_key], re.I) for rgx in toskip)):
                yield item
    except TypeError:
        yield None


def list_reorder(contents_json, showtitle, year=False, sync_type=False):
    """Return a list of elements reordered by number id."""
    reordered = [''] * len(contents_json)
    years = []
    stored_title = None
    stored_season = None
    for index, item in enumerate(contents_json):
        # TODO: check if logic is real necessary, test is for all languages eficient
        STR_SEASON_CHECK = re_search(
            item['label'],
            ['season', 'temporada', r'S\d{1,4}']
        )
        if sync_type != 'all_items':
            if sync_type == 'movie' and item['type'] == 'movie':
                pass
            elif sync_type == 'tvshow':
                tvshow_search = [
                    'tvshow',
                    'season',
                    'episode',
                    'unknown',
                    'directory'
                ]
                if re_search(item['type'], tvshow_search):
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
            reordered[item['number'] - 1] = item
        else:
            # CRUNCHYROLL
            if 'crunchyroll' in item['file']:
                # CRUNCHYROLL SHOW DIRECTORY
                if item['filetype'] == 'directory':
                    if not re_search(item['type'], ['tvshow', 'unknown']):
                        _regex = [
                            r'(status|mode)\=(Continuing|status|Completed|series)'
                        ]
                        if not re_search(item['file'], _regex):
                            item['type'] = 'tvshow'
                            del item['episode']
                            del item['season']
                            del item['title']

                            reordered[item['number'] - 1] = item
                    # CRUNCHYROLL SEASON DIRECTORY
                    if item['type'] == 'unknown':
                        if re_search(item['file'], ['season=']):
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
                    if item['episode'] == -1 and item['season'] == -1:
                        if STR_SEASON_CHECK is False:
                            if re_search(item['type'], ['tvshow']):
                                item['type'] = 'tvshow'
                                item['showtitle'] = item['label']
                                del item['episode']
                                del item['season']
                                reordered[item['number'] - 1] = item
                    # AMAZON SEASON DIRECTORY
                    if item['type'] == 'unknown' and item['season'] != -1:
                        if STR_SEASON_CHECK is True:
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
                    elif item['filetype'] == 'directory':
                        if item['episode'] == -1:
                            if item['season'] != -1:
                                if STR_SEASON_CHECK is False:
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
                    if item['episode'] != -1:
                        if item['season'] != -1:
                            if item['type'] == 'episode':
                                try:
                                    years.append(item['year'])
                                except KeyError:
                                    pass
                                reordered[item['episode'] - 1] = item
            # DISNEY
            if 'disney' in item['file']:
                # DISNEY SHOW DIRECTORY
                if item['filetype'] == 'directory':
                    if item['type'] == 'tvshow':
                        if item['season'] == -1:
                            if STR_SEASON_CHECK is False:
                                item['showtitle'] = item['title']
                                item['type'] = 'tvshow'
                                del item['episode']
                                del item['season']
                                reordered[item['number'] - 1] = item
                    # DISNEY SEASON DIRECTORY
                    if item['type'] == 'unknown':
                        if STR_SEASON_CHECK is True:
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
                    if item['type'] == 'episode':
                        try:
                            years.append(item['year'])
                        except KeyError:
                            pass
                        reordered[item['episode'] - 1] = item
            # NETFLIX
            if 'netflix' in item['file']:
                if item['filetype'] == 'directory':
                    # NETFLIX SHOW DIRECTORY
                    if re_search(item['type'], ['tvshow']):
                        if not re_search(item['file'], ['season', 'episode']):
                            del item['episode']
                            del item['season']
                            reordered[item['number'] - 1] = item
                    # NETFLIX SEASON DIRECTORY
                    if item['type'] == 'unknown':
                        if re_search(item['file'], ['show', 'season']):
                            if not re_search(item['file'], ['episode']):
                                if STR_SEASON_CHECK is True:
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
                    if item['type'] == 'episode':
                        if re_search(item['file'], ['show', 'season', 'episode']):
                            try:
                                years.append(item['year'])
                            except KeyError:
                                pass
                            if item['episode'] != item['number']:
                                item['episode'] = item['number']
                                reordered[item['number'] - 1] = item
                            else:
                                reordered[item['episode'] - 1] = item
            # this part of code detect episodes with < 30 in season with 'Next Page'
            # works with CRUNCHYROLL, but can work for all
            if item['filetype'] == 'file' and item['type'] == 'episode':
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
        if item:
            try:
                loweryear = min(years)
                item['year'] = loweryear
            except (KeyError, ValueError):
                pass
            yield item


def selected_list(results):
    """Open a dialog and show entries to user select."""
    mapped = dict()
    for index, item in enumerate(results):
        mapped[index] = item
    selection = xbmcgui.Dialog().multiselect(
        'Escolha:',
        list(
            x['label'] for x in skip_filter(
                results,
                'label',
                SKIP_STRINGS
            )
        )
    )
    try:
        for index in selection:
            yield mapped[index]
    except TypeError:
        yield None


def load_directory_items(progressdialog, _path, recursive=False,
                         allow_directories=False, depth=1, showtitle=False,
                         season=False, year=False, sync_type=False):
    """Load items in a directory using the JSON-RPC interface."""
    if RECURSION_LIMIT and depth > RECURSION_LIMIT:
        yield []
    results = execute_json_rpc(
        'Files.GetDirectory',
        _path=_path)['result']['files']
    if sync_type == 'filter':
        sync_type = 'all_items'
        results = list(selected_list(results))
    try:
        filtered = list(skip_filter(
            results,
            'label',
            SKIP_STRINGS
        )
        )
        listofitems = list(
            list_reorder(
                filtered,
                showtitle=showtitle,
                year=year,
                sync_type=sync_type
            )
        )
    except (KeyError, TypeError):
        listofitems = []

    if not allow_directories:
        for item in listofitems:
            if item and item['filetype'] == 'file':
                yield item

    directories = []
    for index, item in enumerate(listofitems):
        if progressdialog.iscanceled() is True:
            progressdialog.close()
            break
        percent = 100 * index / len(listofitems)
        if item['type'] == 'movie':
            progressdialog.update(
                int(percent),
                'Processando items:\n%s' % item['title']
            )
            xbmc.sleep(200)
            if item:
                yield item
        else:
            if season is not False:
                item['season'] = season
            if year is not False:
                item['year'] = year
                # if content is a directory will be added to directories list
            if (item['filetype'] == 'directory' and
                    item['type'] == 'tvshow' or
                    item['type'] == 'season'):
                showtitle = item['showtitle']
                progressdialog.update(
                    int(percent), 'Coletando itens no diretorio!\n%s' % item['label'])
                xbmc.sleep(200)
                directories.append(item)
                # if content is a episode, will be stored with yeld
            if item['type'] == 'episode':
                progressdialog.update(
                    int(percent), 'Processando items:\n%s' % item['label'])
                xbmc.sleep(100)
                item['showtitle'] = showtitle
                if item:
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
                _path=_dir['file'],
                recursive=recursive,
                allow_directories=allow_directories,
                depth=depth + 1,
                showtitle=title,
                season=season,
                year=year,
                sync_type=sync_type
            ))
            for new in new_items:
                if item:
                    yield new


def notification(message, time=3000, icon=join(ADDON_PATH, 'ntf_icon.png')):
    """Provide a shorthand for xbmc builtin notification with addon name."""
    xbmcgui.Dialog().notification(
        ADDON_NAME,
        message,
        icon,
        time,
        True
    )


def tojs(data, filename):
    """Function to create a json file."""
    try:
        with open(join(expanduser('~/'), filename) + '.json', 'a+') as f:
            f.write(str(json.dumps(data, indent=4, sort_keys=True)))
            f.close()
    except AttributeError:
        pass


def getlocalizedstring(string_id):
    """Function to get call getLocalizedString and deal with unicodedecodeerrors."""
    return str(ADDON.getLocalizedString(string_id))


def title_with_color(label, year=None, color='mediumslateblue'):
    """Create a string to use in title Dialog().select."""
    # COLORS: https://github.com/xbmc/xbmc/blob/master/system/colors.xml
    # TODO: this function can be better, maybe led generic,
    # now, this func add color and year to movie title,
    # and any of this actions can be splited
    if year:
        return str('[COLOR %s][B]%s (%s)[/B][/COLOR]' % (color, label, year))
    return str('[COLOR %s][B]%s[/B][/COLOR]' % (color, label))


def colored_str(string, color='mediumslateblue'):
    """
    Return string formated with a selected color.
    lawngreen
    mediumseagreen
    """
    # COLORS: https://github.com/xbmc/xbmc/blob/master/system/colors.xml
    return str('[COLOR %s][B]%s[/B][/COLOR]' % (color, string))
