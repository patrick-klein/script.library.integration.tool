#!/usr/bin/python
# -*- coding: utf-8 -*-

'''Group of Shortcut functions to manipulate and create all type of content'''

from resources.lib.items.movie import MovieItem
from resources.lib.items.episode import EpisodeItem

from resources.lib.items.contentmanager import ContentManagerShow
from resources.lib.items.contentmanager import ContentManagerMovie


def build_json_item(item):
    '''Shortcut to convert a database item into a json'''
    formated_json = dict()
    keys = [
            'file',
            'title',
            'type',
            'state',
            'year'
        ]
    if len(item) == 8:
        # extra keys to convert show from db
        keys += [
            'showtitle',
            'season',
            'episode'
        ]
    for key, value in zip(keys, item):
        formated_json[key] = value
    return formated_json


def build_contentitem(jsonitem):
    """Shortcut to return a MovieItem or EpisodeItem json"""
    if jsonitem['type'] == 'movie':
        return MovieItem(
            jsonitem=jsonitem
        ).returasjson()
    if jsonitem['type'] in ['tvshow', 'episode']:
        return EpisodeItem(
            jsonitem=jsonitem
        ).returasjson()
    elif jsonitem['type'] == 'music':
        # TODO: add music
        raise ValueError('Not implemented yet, music')
    raise ValueError('Unrecognized type in Content query')


def build_contentmanager(database, jsonitem):
    '''Shortcut to create a ContentManager object'''
    if jsonitem['type'] == 'movie':
        return ContentManagerMovie(database, jsonitem)
    if jsonitem['type'] in ['tvshow', 'episode']:
        return ContentManagerShow(database, jsonitem)
    elif jsonitem['type'] == 'music':
        raise ValueError('Not implemented yet, music')
