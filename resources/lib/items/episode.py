#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Defines the EpisodeItem class
'''

import os
import re
from glob import glob

import xbmc
from bs4 import BeautifulSoup

import resources.lib.database_handler  # Need to do absolute import to avoid circular import error
import resources.lib.utils as utils
from .content import ContentItem


class EpisodeItem(ContentItem):
    ''' Contains information about a TV show episode from the database,
    and has necessary functions for managing item '''

    def __init__(self, path, eptitle, mediatype, show_title, season=None, epnumber=None, year=None):
        super(EpisodeItem, self).__init__(path, eptitle, mediatype)
        self.link_stream_path = path
        self.show_title = str(show_title)
        if season == None:
            self.season = 1
        else:
            self.season = int(season)

        self.epnumber = int(epnumber)
        self.episode_title = eptitle.encode('utf-8')
        self.year = year
        self._clean_show_title = None

    @property
    def seasondir(self):
        return ('Season %s' % (self.season))

    @property
    def epsodeid(self):
        if self.season <= 9:
            season = ('S0%s' % self.season)
        else:
            season = ('S%s' % self.season)

        if self.epnumber <= 9:
            ep = ('E0%s' % self.epnumber)
        else:
            ep = ('E%s' % self.epnumber)
        return ('%s%s' % (season, ep))

    @property
    def clean_show_title(self):
        ''' Show title with problematic characters removed '''
        if not self._clean_show_title:
            self._clean_show_title = utils.clean_name(self.show_title)
        return self._clean_show_title

    @property
    def managed_show_dir(self):
        if not self._managed_dir:
            self._managed_dir = os.path.join(
                utils.MANAGED_FOLDER, 'ManagedTV', self.clean_show_title
            )
        return self._managed_dir

    @property
    def metadata_show_dir(self):
        if not self._metadata_show_dir:
            self._metadata_show_dir = os.path.join(utils.METADATA_FOLDER, 'TV', self.clean_show_title)
        return self._metadata_show_dir
    # json exemple
    # {
    #     "episode_title": "Filmed Before a Live Studio Audience",
    #     "episode_title_with_id": "S01E01 - Filmed Before a Live Studio Audience",
    #     "episodenum": 1,
    #     "epsodeid": "S01E01",
    #     "link_stream_path": "plugin://slyguy.disney.plus/?_=play&_play=1&content_id=964f19ae-0a75-4b53-b23a-e8f8ea0186fe&profile_id=0e96b0c7-8ffc-4447-bbc6-882d6b0098ec&sync=1",
    #     "metadata_show_dir": "/media/luiz/HD/MIDIA/managed/Metadata/TV/WandaVision",
    #     "seasondir": "Season 1",
    #     "seasonnum": 1,
    #     "managed_show_dir": "/media/luiz/HD/MIDIA/managed/ManagedTV/WandaVision",
    #     "show_title": "WandaVision",
    #     "year": "2021"
    # }

    @utils.logged_function
    def returasjson(self):
        try:
            return {
                'link_stream_path': self.link_stream_path,
                'show_title': self.clean_show_title,
                'episode_title_with_id': ' - '.join([self.epsodeid, self.clean_eptitle]),
                'episode_title': self.clean_eptitle,
                'seasonnum': self.season,
                'episodenum': self.epnumber,
                'epsodeid': self.epsodeid,
                'seasondir': self.seasondir,
                'managed_show_dir': self.managed_show_dir,
                'metadata_show_dir': self.metadata_show_dir,
                'year': self.year,
            }
        except Exception as e:
            raise e