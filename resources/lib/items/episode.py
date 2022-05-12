# -*- coding: utf-8 -*-
# pylint: disable=broad-except

"""Defines the EpisodeItem class."""

Import xbmc 
from os.path import join

from resources.lib.log import log_msg
from resources.lib.log import logged_function

from resources.lib.utils import MANAGED_FOLDER
from resources.lib.manipulator import Cleaner


class EpisodeItem():
    """Class to build information aboult shows."""

    def __init__(self, jsonitem, year=None):
        """__init__ EpisodeItem."""
        self.cleaner = Cleaner()
        self.jsonitem = jsonitem
        self.arg_year = year

    def file(self):
        """Return file."""
        return self.jsonitem['file']

    def title(self):
        """Return title."""
        return self.cleaner.title(
            showtitle=self.jsonitem['showtitle'],
            title=self.jsonitem['title']
        )

    def showtitle(self):
        """Show title with problematic characters removed."""
        return self.cleaner.showtitle(
            self.jsonitem['showtitle']
        )

    def season(self):
        """Show title with problematic characters removed."""
        season = self.jsonitem['season']
        if not season:
            return 1
        return int(season)

    def episode(self):
        """Show title with problematic characters removed."""
        episode = self.jsonitem['episode']
        if not episode:
            return 1
        return int(episode)

    def year(self):
        """Show title with problematic characters removed."""
        return self.arg_year if self.arg_year else self.jsonitem['year']

    def season_dir(self):
        """retirn season_dir."""
        return 'Season %s' % (self.season())

    def episode_id(self):
        """Return episode_id."""
        season = ('S%s' % self.season())
        ep = ('E%s' % self.episode())

        if self.season() <= 9:
            season = ('S0%s' % self.season())

        if self.episode() <= 9:
            ep = ('E0%s' % self.episode())
        return '%s%s' % (season, ep)

    def managed_show_dir(self):
        """Return managed_show_dir."""
        return join(
            MANAGED_FOLDER, 'tvshows', self.showtitle()
        )

    @logged_function
    def returasjson(self):
        """Return a dict with all information about tvshow."""
        try:
            return {
                'file': self.file(),
                'showtitle': self.showtitle(),
                'episode_title_with_id': f'{self.episode_id()} - {self.title()}',
                'title': self.title(),
                'episode': self.episode(),
                'episode_id': self.episode_id(),
                'season': self.season(),
                'season_dir': self.season_dir(),
                'managed_show_dir': self.managed_show_dir(),
                'year': self.year(),
                'type': 'tvshow'
            }
        except Exception as error:
            log_msg(f'EpisodeItem.returasjson: {error}')
        return None
