
# This strings will be used to ignore itens in show diretectories

import re
import json

from os.path import join
from os.path import expanduser

import xbmc
import xbmcgui

from resources import ADDON
from resources import ADDON_NAME
from resources import ADDON_PATH


SKIP_STRINGS = [
    'resumo',
    'suggested',
    'extras',
    # 'trailer',
    r'\#(?:\d{1,5}\.\d{1,5}|SP)',
]


def re_search(string, tosearch=None):
    """Function check if string exist with re."""
    tosearch = tosearch if isinstance(tosearch, list) else [tosearch]
    return bool(
        any(
            re.search(
                rgx,
                string,
                re.I
            ) for rgx in tosearch
        )
    )


def skip_filter(contents_json, _key, toskip):
    """Function to iterate jsons in a list and filter by key with re."""
    try:
        for item in contents_json:
            if not bool(any(re.search(rgx, item[_key], re.I) for rgx in toskip)):
                yield item
    except TypeError:
        yield None


def is_season(string):
    """Function to check if item is a season."""
    return bool(
        re_search(
            string,
            ['season', 'temporada', r'S\d{1,4}']
        )
    )


def notification(message, time=3000, icon=join(ADDON_PATH, 'ntf_icon.png')):
    """Provide a shorthand for xbmc builtin notification with addon name."""
    xbmcgui.Dialog().notification(
        ADDON_NAME,
        str(message),
        icon,
        time,
        True
    )


def savetojson(data):
    """Function to create a json file."""
    try:
        filename = join(expanduser('~/'), 'json_result.json')
        with open(filename, 'a+') as jsonoutput:
            jsonoutput.write(str(json.dumps(data, indent=4, sort_keys=True)))
            jsonoutput.close()
    except AttributeError:
        pass


def getstring(string_id):
    """Shortcut function to return string from String ID."""
    return str(ADDON.getLocalizedString(string_id))


def title_with_color(label, year=None, colorname='mediumslateblue'):
    """Create a string to use in title Dialog().select."""
    # COLORS: https://github.com/xbmc/xbmc/blob/master/system/colors.xml
    # TODO: this function can be better, maybe led generic,
    # now, this func add color and year to movie title,
    # and any of this actions can be splited
    if year:
        return str('[COLOR %s][B]%s (%s)[/B][/COLOR]' % (colorname, label, year))
    return str('[COLOR %s][B]%s[/B][/COLOR]' % (colorname, label))


def color(string, colorname='mediumslateblue'):
    """
    Return string formated with a selected color.
    lawngreen
    mediumseagreen
    """
    # COLORS: https://github.com/xbmc/xbmc/blob/master/system/colors.xml
    return str('[COLOR %s]%s[/COLOR]' % (colorname, string))


def bold(string):
    """
    Return string formated with a bold.
    """
    return str('[B]%s[/B]' % (string))

# in future path arg will select the clean method


def videolibrary(method, database='video'):
    """A dedicated method to performe jsonrpc VideoLibrary.Scan or VideoLibrary."""
    command = {
        'scan': 'CleanLibrary(%s)' % database,
        'clean': 'UpdateLibrary(%s)' % database
    }
    xbmc.executebuiltin(command[method])
