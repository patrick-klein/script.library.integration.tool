# -*- coding: utf-8 -*-
# pylint: disable=broad-except

"""Contains various constants and utility functions used thoughout the addon."""

import re
import json

from os.path import join

import xbmc
import xbmcgui
import xbmcvfs

from resources.lib.misc import is_season
from resources.lib.misc import re_search
from resources.lib.misc import getstring
from resources.lib.misc import skip_filter
from resources.lib.misc import notification
from resources.lib.misc import SKIP_STRINGS

from resources import ADDON
from resources import ADDON_ID
from resources import RECURSION_LIMIT
from resources import USING_CUSTOM_MANAGED_FOLDER

from resources.lib.log import log_msg
from resources.lib.filesystem import isdir, mkdir
from resources.lib.dialog_select import Select
from resources.lib.version import check_version_file


if USING_CUSTOM_MANAGED_FOLDER:
    MANAGED_FOLDER = xbmcvfs.validatePath(ADDON.getSetting('managed_folder'))
else:
    MANAGED_FOLDER = xbmcvfs.translatePath(
        f"special://userdata/addon_data/{ADDON_ID}/"
    )

DATABASE_PATH = join(MANAGED_FOLDER, 'managed.db')

def check_managed_folder():
    """Check if the managed folder is configured."""
    if not xbmcvfs.exists(MANAGED_FOLDER):
        STR_CHOOSE_FOLDER = f'Created managed folder "{MANAGED_FOLDER}"'
        mkdir(MANAGED_FOLDER)
        log_msg(STR_CHOOSE_FOLDER, xbmc.LOGERROR)


def create_content_dirs():
    """Create subdirs in managed folder if not exist."""
    # Create subfolders if they don't exist
    folders = [
        'movies',
        'tvshows',
    ]
    # MANAGED_FOLDER
    created_folders = False
    for folder in folders:
        dest_dir = join(MANAGED_FOLDER, folder)
        if not isdir(dest_dir):
            # log_msg('Created diretory {}'.format(dest_dir), loglevel=xbmc.LOGINFO)
            notification(f'Created diretory {dest_dir}')
            mkdir(dest_dir)
            created_folders = True

    if created_folders:
        STR_SUBFOLDERS_CREATED = getstring(32127)
        notification(STR_SUBFOLDERS_CREATED)
        # TODO: Add video sources here
        xbmc.sleep(1)


def entrypoint(func):
    """Decorator to perform actions required for entrypoints."""
    def wrapper(*args, **kwargs):
        """function wrapper."""
        check_version_file()
        check_managed_folder()
        create_content_dirs()
        return func(*args, **kwargs)
    return wrapper


def jsonrpc_generic(method, _path):
    """
    Execute a JSON-RPC for command.

    See https://kodi.wiki/view/JSON-RPC_API/v12 for methods and params.
    """
    return json.loads(
        xbmc.executeJSONRPC(
            json.dumps({
                'jsonrpc': '2.0',
                "method": method,
                "params": {
                    'directory': _path,
                }, 'id': 1
            },)
        )
    )


def jsonrpc_getdirectory(_path):
    """
    Execute a JSON-RPC with parameter Files.GetDirectory.

    See https://kodi.wiki/view/JSON-RPC_API/v12 for methods and params.
    """
    try:
        return json.loads(
            xbmc.executeJSONRPC(
                json.dumps({
                    'jsonrpc': '2.0',
                    "method": 'Files.GetDirectory',
                    "params": {
                        'directory': _path,
                        'properties': [
                            'art',
                            'fanart',
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
                }
                )
            )
        )['result']['files']
    except KeyError:
        log_msg('KeyError in return of JSONRPC.')


def list_reorder(contents_json, showtitle, sync_type=False):
    """Return a list of elements reordered by number id."""
    reordered = [''] * len(contents_json)
    years = []
    for index, item in enumerate(contents_json):
        # TODO: check if logic is real necessary, test is for all languages eficient
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
            item['year'] = 0

        # MOVIES: detect movies in dir
        if item['filetype'] == 'file' and item['type'] == 'movie':
            del item['episode']
            del item['season']
            del item['showtitle']
            reordered[index] = item
        else:
            # CRUNCHYROLL
            if 'crunchyroll' in item['file']:
                # CRUNCHYROLL SHOW DIRECTORY
                if item['filetype'] == 'directory':
                    if re_search(item['file'], r'mode\=series'):
                        if item['season'] == -1:
                            item['type'] = 'tvshow'
                            del item['episode']
                            del item['season']
                            del item['title']
                            reordered[index] = item
                    # CRUNCHYROLL SEASON DIRECTORY
                    if re_search(item['file'], r'mode\=episodes'):
                        item['type'] = 'season'
                        if showtitle:
                            item['showtitle'] = showtitle
                        reordered[index] = item
                elif item['filetype'] == 'file':
                    # CRUNCHYROLL EPISODE FILE
                    if re_search(item['file'], r'mode\=videoplay'):
                        item['episode'] = item['number']
                        item['type'] = 'episode'
                        if item['season'] == 0 or item['season'] == -1:
                            item['season'] = 1
                        else:
                            item['season'] = int(
                                re.findall(
                                    r'season\=(.+?)',
                                    item['file'])[0]
                            )
                        # TODO: Maybe year can be collected from file
                        # with regex but aparently not all shows has year=XXXX info
                        # maybe premiered=XXXX or aired=XXXX can work
                        try:
                            years.append(item['year'])
                        except KeyError:
                            pass
                        reordered[index] = item
            # AMAZON
            if 'amazon' in item['file']:
                if item['filetype'] == 'directory':
                    # AMAZON SHOW DIRECTORY
                    if item['episode'] == -1:
                        if not is_season(item['label']):
                            if re_search(item['type'], ['tvshow', 'unknown']):
                                item['type'] = 'tvshow'
                                item['showtitle'] = item['label']
                                del item['episode']
                                del item['season']
                                reordered[index] = item
                    # AMAZON SEASON DIRECTORY
                    if is_season(item['label']):
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
                            if not is_season(item['label']):
                                item['showtitle'] = item['title']
                                item['type'] = 'tvshow'
                                del item['episode']
                                del item['season']
                                reordered[index] = item
                    # DISNEY SEASON DIRECTORY
                    if item['type'] == 'unknown':
                        if is_season(item['label']):
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
                            reordered[index] = item
                    # NETFLIX SEASON DIRECTORY
                    if item['type'] == 'unknown':
                        if re_search(item['file'], ['show', 'season']):
                            if not re_search(item['file'], ['episode']):
                                if is_season(item['label']):
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
                            if item['episode'] != item['number']:
                                item['episode'] = item['number']
                                reordered[index] = item
                            else:
                                reordered[item['episode'] - 1] = item
                            try:
                                years.append(item['year'])
                            except KeyError:
                                pass
            # HBOMAX
            if 'slyguy.hbo.max' in item['file']:
                # HBOMAX SHOW DIRECTORY
                if item['filetype'] == 'directory':
                    if re_search(item['type'], ['tvshow', 'unknown']):
                        if item['season'] == -1:
                            if not is_season(item['label']):
                                item['showtitle'] = item['title']
                                item['type'] = 'tvshow'
                                del item['episode']
                                del item['season']
                                reordered[index] = item
                    # HBOMAX SEASON DIRECTORY
                    if item['type'] == 'unknown':
                        if is_season(item['label']):
                            item['showtitle'] = showtitle
                            del item['episode']
                            item['type'] = 'season'
                            item['season'] = item['number']
                            try:
                                years.append(item['year'])
                            except KeyError:
                                pass
                            reordered[item['season'] - 1] = item
                elif item['filetype'] == 'file':
                    # HBOMAX EPISODE FILE
                    if item['type'] == 'episode':
                        try:
                            years.append(item['year'])
                        except KeyError:
                            pass
                        try:
                            reordered[item['episode'] - 1] = item
                        except IndexError:
                            pass
            # CRACKLE
            if 'crackle' in item['file']:
                # CRACKLE SHOW DIRECTORY
                if item['filetype'] == 'directory':
                    if item['type'] == 'tvshow':
                        if item['season'] == -1:
                            if not is_season(item['label']):
                                item['showtitle'] = item['title']
                                item['type'] = 'tvshow'
                                del item['episode']
                                del item['season']
                                reordered[index] = item
                elif item['filetype'] == 'file':
                    # CRACKLE EPISODE FILE
                    if item['type'] == 'episode':
                        try:
                            years.append(item['year'])
                        except KeyError:
                            pass
                        try:
                            reordered[item['episode'] - 1] = item
                        except IndexError:
                            pass
            # PARAMOUNTPLUS
            if 'slyguy.paramount.plus' in item['file']:
                # PARAMOUNTPLUS SHOW DIRECTORY
                if item['filetype'] == 'directory':
                    if re_search(item['type'], ['tvshow', 'unknown']):
                        if item['season'] == -1:
                            if not is_season(item['label']):
                                item['showtitle'] = item['title']
                                item['type'] = 'tvshow'
                                del item['episode']
                                del item['season']
                                reordered[index] = item
                    # PARAMOUNTPLUS SEASON DIRECTORY
                    if item['type'] == 'unknown':
                        if is_season(item['label']):
                            item['showtitle'] = showtitle
                            del item['episode']
                            item['type'] = 'season'
                            item['season'] = item['number']
                            reordered[item['season'] - 1] = item
                elif item['filetype'] == 'file':
                    # PARAMOUNTPLUS EPISODE FILE
                    if item['type'] == 'episode':
                        try:
                            years.append(item['year'])
                        except KeyError:
                            pass
                        try:
                            reordered[item['episode'] - 1] = item
                        except IndexError:
                            pass
            # RAIPLAY
            if 'plugin.video.raitv' in item['file']:
                if item['filetype'] == 'directory':
                    # RAIPLAY SHOW DIRECTORY
                    if re_search(item['label'], 'Episodi'):
                        item['type'] = 'tvshow'
                        del item['episode']
                        del item['season']
                        reordered[index] = item
                elif item['filetype'] == 'file':
                    # RAIPLAY EPISODE FILE
                    item['type'] = 'episode'
                    try:
                        if item['episode'] == 0:
                            item['episode'] = item['number']
                        reordered[item['episode'] - 1] = item
                    except IndexError:
                        pass
    for item in reordered:
        if item:
            try:
                loweryear = min(years)
                item['year'] = loweryear
            except (KeyError, ValueError):
                pass
            yield item


def user_selection_menu(results):
    """Open a dialog and show entries to user select."""
    # ___ TODO: all select and multselect menus need
    # something like this to facilitate reordering
    # in alphabetical order.
    sorted_labels = sorted([i['label'] for i in results])
    _sorted = []
    for i in sorted_labels:
        for r in results:
            if r['label'] == i:
                _sorted.append(r)
    # ___
    selected_itens = xbmcgui.Dialog().multiselect(
        'Escolha:',
        [x['label'] for x in _sorted]
    )
    if selected_itens:
        for index_int in selected_itens:
            yield _sorted[index_int]


crunchyroll_language_selected = None


def crunchyroll_language_menu(results):
    """Menu to select language for crunchyroll."""
    global crunchyroll_language_selected
    # TODO: verificar a possibilidade de
    # adicionar uma opção nas configurações.
    lang_regex = r'Dublado|\(.+? Dub\)|\(Leg\)|\(Dub.+?\)'
    try:
        for item in results:
            is_language_episode = bool(
                any(re_search(lang_regex, i['label']) for i in results))
            if 'crunchyroll' in item['file'] and item['filetype'] == 'directory':
                if re_search(item['file'], r'mode\=series'):
                    yield item
                elif re_search(item['file'], r'mode\=episodes'):
                    if is_language_episode:
                        if not crunchyroll_language_selected:
                            sel = Select(
                                heading="Select one language:",
                                turnbold=True
                            )
                            sel.items(
                                [i['label'] for i in results]
                            )
                            selection = sel.show(back=False)['str']
                            try:
                                crunchyroll_language_selected = re.findall(
                                    lang_regex, selection, re.I)[0]
                            except IndexError:
                                crunchyroll_language_selected = selection
                    else:
                        yield item
            elif not is_language_episode:
                yield item
    except Exception as error:
        log_msg('crunchyroll_language_menu error: %s' % error)
    if crunchyroll_language_selected:
        for lang_dir in results:
            if not '(' in crunchyroll_language_selected:
                if crunchyroll_language_selected == lang_dir['label']:
                    yield lang_dir
            elif '(' in crunchyroll_language_selected:
                if crunchyroll_language_selected in lang_dir['label']:
                    yield lang_dir


def load_directory_items(progressdialog, _path, recursive=False,
                         allow_directories=False, depth=1, showtitle=False,
                         season=False, year=False, sync_type=False):
    """Load items in a directory using the JSON-RPC interface."""
    if RECURSION_LIMIT and depth > RECURSION_LIMIT:
        yield []
    results = jsonrpc_getdirectory(
        _path=_path
    )
    if sync_type == 'filter':
        sync_type = 'all_items'
        results = list(user_selection_menu(results))
    try:
        results = list(skip_filter(
            results,
            'label',
            SKIP_STRINGS
        )
        )
        results = list(
            list_reorder(
                list(crunchyroll_language_menu(results)),
                showtitle=showtitle,
                sync_type=sync_type
            )
        )
    except (KeyError, TypeError) as error:
        results = []
        log_msg("INFO ERROR -> %s -> %s" % (error, results))
    if not allow_directories:
        for item in results:
            if item and item['filetype'] == 'file':
                yield item
    directories = []
    for index, item in enumerate(results):
        if item['type'] == 'movie':
            progressdialog.update_progressdialog(
                index / len(results),
                'Processando items:\n%s' % item['title']
            )
            if item:
                yield item
        else:
            if season:
                item['season'] = season
            if year:
                item['year'] = year
            # if content is a directory will be added to directories list
            if item['filetype'] == 'directory':
                if re_search(item['type'], ['season', 'tvshow']):
                    showtitle = item['showtitle']
                    progressdialog.update_progressdialog(
                        index / len(results),
                        'Coletando itens no diretorio!\n%s' % item['label']
                    )
                    directories.append(item)
            # if content is a episode, will be stored with yeld
            if item['type'] == 'episode':
                # change type to 'tvshow' to padronize in build_contentitem
                item['type'] = 'tvshow'
                progressdialog.update_progressdialog(
                    index / len(results),
                    'Processando items:\n%s' % item['label']
                )
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
            new_items = list(
                load_directory_items(
                    progressdialog=progressdialog,
                    _path=_dir['file'],
                    recursive=recursive,
                    allow_directories=allow_directories,
                    depth=depth + 1,
                    showtitle=title,
                    season=season,
                    year=year,
                    sync_type=sync_type
                )
            )
            for new in new_items:
                if item:
                    yield new
