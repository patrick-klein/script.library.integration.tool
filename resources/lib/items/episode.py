#!/usr/bin/python
# -*- coding: utf-8 -*-

'''Defines the EpisodeItem class'''
from os.path import join

from resources.lib.utils import MANAGED_FOLDER
from resources.lib.utils import METADATA_FOLDER
from resources.lib.utils import clean_name
from resources.lib.log import logged_function

from resources.lib.abs.item import ABSItemShow


class EpisodeItem(ABSItemShow):
    '''Class to build information aboult shows'''
        

    @property


    @property


    @property
        '''Show title with problematic characters removed'''


    @property
        '''Show title with problematic characters removed'''
        if self._season == None:
            return 1
        else:
            return int(self._season)


    @property
        '''Show title with problematic characters removed'''
            return  1
        else:


    @property
    def year(self):
        '''Show title with problematic characters removed'''
        return self._year


    @property
    def season_dir(self):


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
                MANAGED_FOLDER, 'ManagedTV', self.show_title
            )
        return self._managed_dir


    @property
    def metadata_show_dir(self):
        if not self._metadata_show_dir:
            self._metadata_show_dir = join(METADATA_FOLDER, 'TV', self.show_title)
        return self._metadata_show_dir


    @logged_function
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
