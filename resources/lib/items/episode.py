#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Defines the EpisodeItem class
'''
from os.path import join
import resources.lib.utils as utils
from .content import ContentItemShow


class EpisodeItem(ContentItemShow):
    ''' Contains information about a TV show episode from the database,
    and has necessary functions for managing item '''

    def __init__(self, link_stream_path, title, mediatype, show_title=None, season=None, epnumber=None, year=None):
        super(EpisodeItem, self).__init__(link_stream_path, title, mediatype, show_title, season, epnumber, year)
        self._link_stream_path = link_stream_path
        try:
            self._episode_title = title
        except UnicodeEncodeError:
            self._episode_title = title

        self._episode_title = title
        # mediatype
        self._show_title = show_title
        self._season = season
        self._episode_number = epnumber
        self._year = year
        

    @property
    def link_stream_path(self):
        return self._link_stream_path

    @property
    def episode_title(self):
        return utils.clean_name(self._episode_title)
    
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
    def episode_number(self):
        ''' Show title with problematic characters removed '''
        if self._episode_number == None:
            return  1
        else:
            return int(self._episode_number)

    @property
    def year(self):
        ''' Show title with problematic characters removed '''
        return self._year
    # 
    # # 
    @property
    def season_dir(self):
        return ('Season %s' % (self.season_number))

    @property
    def episode_id(self):
        if self.season_number <= 9:
            season = ('S0%s' % self.season_number)
        else:
            season = ('S%s' % self.season_number)

        if self.episode_number <= 9:
            ep = ('E0%s' % self.episode_number)
        else:
            ep = ('E%s' % self.episode_number)
        return ('%s%s' % (season, ep))

    @property
    def managed_show_dir(self):
        if not self._managed_dir:
            self._managed_dir = join(
                utils.MANAGED_FOLDER, 'ManagedTV', self.show_title
            )
        return self._managed_dir

    @property
    def metadata_show_dir(self):
        if not self._metadata_show_dir:
            self._metadata_show_dir = join(utils.METADATA_FOLDER, 'TV', self.show_title)
        return self._metadata_show_dir

    @utils.logged_function
    def returasjson(self):
        try:
            return {
                'link_stream_path': self.link_stream_path,
                'show_title': self.show_title,
                'episode_title_with_id': ' - '.join([self.episode_id, self.episode_title]),
                'episode_title': self.episode_title,
                'episode_number': self.episode_number,
                'episode_id': self.episode_id,
                'season_number': self.season_number,
                'season_dir': self.season_dir,
                'managed_show_dir': self.managed_show_dir,
                'metadata_show_dir': self.metadata_show_dir,
                'year': self.year,
                'type': 'tvshow'
            }
        except Exception as e:
            raise e
