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

    def __init__(self, link_stream_path, title, mediatype, show_title=None, season=None, epnumber=None, year=None):
        super(EpisodeItem, self).__init__(link_stream_path, title, mediatype, show_title, season, epnumber, year)
        self._link_stream_path = link_stream_path
        self._episode_title = title.decode('utf-8')
        # mediatype
        self._show_title = show_title
        self._season = season
        self._epsode_number = epnumber
        self._year = year
        

    @property
    def link_stream_path(self):
        return self._link_stream_path

    @property
    def epsode_title(self):
        return utils.clean_name(self._episode_title).encode('utf-8')
    
    @property
    def show_title(self):
        ''' Show title with problematic characters removed '''
        return str(utils.clean_name(self._show_title))

    @property
    def season_number(self):
        ''' Show title with problematic characters removed '''
        if self._season == None:
            return 1
        else:
            return int(self._season)

    @property
    def epsode_number(self):
        ''' Show title with problematic characters removed '''
        if self._epsode_number == None:
            return  1
        else:
            return int(self._epsode_number)

    @property
    def year(self):
        ''' Show title with problematic characters removed '''
        return self._year
    # 
    # # 
    @property
    def seasondir(self):
        return ('Season %s' % (self.season_number))

    @property
    def epsodeid(self):
        if self.season_number <= 9:
            season = ('S0%s' % self.season_number)
        else:
            season = ('S%s' % self.season_number)

        if self.epsode_number <= 9:
            ep = ('E0%s' % self.epsode_number)
        else:
            ep = ('E%s' % self.epsode_number)
        return ('%s%s' % (season, ep))

    @property
    def managed_show_dir(self):
        if not self._managed_dir:
            self._managed_dir = os.path.join(
                utils.MANAGED_FOLDER, 'ManagedTV', self.show_title
            )
        return self._managed_dir

    @property
    def metadata_show_dir(self):
        if not self._metadata_show_dir:
            self._metadata_show_dir = os.path.join(utils.METADATA_FOLDER, 'TV', self.show_title)
        return self._metadata_show_dir

    @utils.logged_function
    def returasjson(self):
        try:
            return {
                'link_stream_path': self.link_stream_path,
                'show_title': self.show_title,
                'episode_title_with_id': ' - '.join([self.epsodeid, self.epsode_title]),
                'episode_title': self.epsode_title,
                'seasonnum': self.season_number,
                'episodenum': self.epsode_number,
                'epsodeid': self.epsodeid,
                'seasondir': self.seasondir,
                'managed_show_dir': self.managed_show_dir,
                'metadata_show_dir': self.metadata_show_dir,
                'year': self.year,
            }
        except Exception as e:
            raise e