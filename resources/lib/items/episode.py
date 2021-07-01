#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Defines the EpisodeItem class."""
from os.path import join

from resources.lib.utils import MANAGED_FOLDER
from resources.lib.utils import METADATA_FOLDER
from resources.lib.manipulator import clean_name
from resources.lib.log import logged_function

from resources.lib.abs.item import ABSItemShow


class EpisodeItem(ABSItemShow):
    """Class to build information aboult shows."""

    def __init__(self, jsonitem, year=None):
        """__init__ EpisodeItem."""
        super(EpisodeItem, self).__init__(jsonitem, year)
        self._file = jsonitem['file']
        self._title = jsonitem['title']
        self._showtitle = jsonitem['showtitle']
        self._season = jsonitem['season']
        self._episode = jsonitem['episode']
        self._year = year if year else jsonitem['year']

    @property
    def file(self):
        """Return file."""
        return self._file

    @property
    def title(self):
        """Return title."""
        return clean_name(self._title)

    @property
    def showtitle(self):
        """Show title with problematic characters removed."""
        return str(clean_name(self._showtitle))

    @property
    def season(self):
        """Show title with problematic characters removed."""
        if self._season == None:
            return 1
        else:
            return int(self._season)

    @property
    def episode(self):
        """Show title with problematic characters removed."""
        if self._episode == None:
            return 1
        else:
            return int(self._episode)

    @property
    def year(self):
        """Show title with problematic characters removed."""
        return self._year

    @property
    def season_dir(self):
        """retirn season_dir."""
        return ('Season %s' % (self.season))

    @property
    def episode_id(self):
        """Return episode_id."""
        if self.season <= 9:
            season = ('S0%s' % self.season)
        else:
            season = ('S%s' % self.season)
        if self.episode <= 9:
            ep = ('E0%s' % self.episode)
        else:
            ep = ('E%s' % self.episode)
        return ('%s%s' % (season, ep))

    @property
    def managed_show_dir(self):
        """Return managed_show_dir."""
        if not self._managed_dir:
            self._managed_dir = join(
                MANAGED_FOLDER, 'tvshows', self.showtitle
            )
        return self._managed_dir

    @property
    def metadata_show_dir(self):
        """Return metadata_show_dir."""
        if not self._metadata_show_dir:
            self._metadata_show_dir = join(
                METADATA_FOLDER, 'TV', self.showtitle)
        return self._metadata_show_dir

    @logged_function
    def returasjson(self):
        """Return a dict with all information about tvshow."""
        try:
            return {
                'file': self.file,
                'showtitle': self.showtitle,
                'episode_title_with_id': ' - '.join([self.episode_id, self.title]),
                'title': self.title,
                'episode': self.episode,
                'episode_id': self.episode_id,
                'season': self.season,
                'season_dir': self.season_dir,
                'managed_show_dir': self.managed_show_dir,
                'metadata_show_dir': self.metadata_show_dir,
                'year': self.year,
                'type': 'tvshow'
            }
        except Exception as e:
            raise e
