# -*- coding: utf-8 -*-

"""Module dedicate to manipulate title."""

import os
import re

from resources.lib.log import logged_function, log_msg

MAPPED_STRINGS = {
    r' \[cc\]': ' ',
    r'\(Legendado\)': ' ',
    r'\(Leg\)': ' ',
    r'\(Dub.+?\)': ' ',
    r'\(.+? Dub\)': ' ',
    r'\((Dublagens|Dubbing) (International|Internacionais)\)': ' ',
    r'\((Dublado|Dubbed) .+?\)': ' ',
    r'\s{1,3}S\d{1,5}\s{1,3}': ' ',
    r'\s{1,4}\#\d{1,6}\s{1,4}\-\s{1,4}': ' ',
    r'\.': ' ',
    r'\:': ' ',
    r'\/': ' ',
    r'\"': ' ',
    r'\$': ' ',
    r'é': 'e',
    # r'Part 1': 'Part One',
    # r'Part 2': 'Part Two',
    # r'Part 3': 'Part Three',
    # r'Part 4': 'Part Four',
    # r'Part 5': 'Part Five',
    # r'Part 6': 'Part Six',
    r'Final Season': ' ',
    r'\s{1,10}': ' ',
}

if os.name == 'nt':
    MAPPED_STRINGS += {
        '?': ' ',
        '<': ' ',
        '>': ' ',
        '\\': ' ',
        '*': ' ',
        '|': ' ',
    }

    # [
    #('+', ''),
    #(',', ''),
    #(';', ''),
    #('=', ''),
    #('[', ''),
    #(']', ''),
    # ]

# TODO: NETFLIX find a way to deal with show with Part 1,
# Part 2 and etc, now, any part will be a season,
# maybe a api call with trakt or tvdb to get episode info is a way


class Cleaner():
    """Class with methods to clear strings from content."""

    def __init__(self) -> None:
        """Cleaner __init__."""
        super().__init__()
        self.strings = MAPPED_STRINGS

    def showtitle(self, showtitle):
        """Function to remove strings from showtitle."""
        for key, val in self.strings.items():
            showtitle = re.sub(key, val, str(showtitle))
        return showtitle.strip()

    def title(self, title, showtitle=None):
        """Function to remove strings and showtitle from title."""
        for key, val in self.strings.items():
            title = re.sub(key, val, str(title))
        return title.replace(self.showtitle(showtitle), ' ').strip()


@logged_function
def cleaner(func):
    '''Decorator that reports the execution time.'''
    def dict_cleaner(*args, **kwargs):
        result = func(*args, **kwargs)
        new_args = [args[0]] if isinstance(args[0], dict) else args[0]
        for item in new_args:
            if 'showtitle' in item:
                showtitle = item['showtitle']
                for key, val in MAPPED_STRINGS.items():
                    showtitle = re.sub(key, val, showtitle)
                    item['showtitle'] = showtitle
                    log_msg('Cleaner ---> %s' % item)
                # if 'type' in item and _type:
                #     item['type'] = 'tvshow'
            if 'title' in item:
                title = item['title']
                for key, val in MAPPED_STRINGS.items():
                    title = re.sub(key, val, title)
                    title = title.replace(showtitle, '')
                    item['title'] = title
                    log_msg('Cleaner ---> %s' % item)
            if 'label' in item:
                label = item['label']
                for key, val in MAPPED_STRINGS.items():
                    label = re.sub(key, val, label)
                    item['label'] = label
                    log_msg('Cleaner ---> %s' % item)
        return result
    return dict_cleaner
 