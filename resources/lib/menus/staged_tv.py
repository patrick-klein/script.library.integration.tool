#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Defines the StagedTVMenu class."""

import os.path

import xbmc  # pylint: disable=import-error
import xbmcgui  # pylint: disable=import-error

from resources import ADDON_NAME

from resources.lib.log import logged_function
from resources.lib.filesystem import remove_dir

from resources.lib.manipulator import clean_name

from resources.lib.utils import bold
from resources.lib.utils import color
from resources.lib.utils import notification
from resources.lib.utils import getlocalizedstring


class StagedTVMenu(object):
    """
    Provide windows for displaying staged tvshows and episodes.

    Provide tools for managing the items.
    """

    def __init__(self, database, progressdialog):
        """__init__ StagedTVMenu."""
        self.database = database
        self.progressdialog = progressdialog

    @logged_function
    def add_all_episodes(self, episodes):
        """Add all episodes from specified show to library."""
        STR_ADDING_ALL_x_EPISODES = getlocalizedstring(32071)
        STR_ALL_x_EPISODES_ADDED = getlocalizedstring(32072)
        showtitle = episodes[0].showtitle
        self.progressdialog._create(
            msg=STR_ADDING_ALL_x_EPISODES % showtitle
        )
        for index, item in enumerate(episodes):
            self.progressdialog._update(
                index / len(episodes),
                '\n'.join([item.showtitle, item.episode_title_with_id]
                          )
            )
            item.add_to_library()
        self.progressdialog._close()
        notification(STR_ALL_x_EPISODES_ADDED % showtitle)

    @logged_function
    def add_all_seasons(self, showtitle):
        """Add all episodes from specified show to library."""
        STR_ADDING_ALL_x_SEASONS = 'Adding all %s seasons...'
        STR_ALL_x_SEASONS_ADDED = 'All %s seasons added'
        staged_seasons = list(
            self.database.get_season_items(
                status='staged',
                showtitle=showtitle
            )
        )
        self.progressdialog._create(
            msg=STR_ADDING_ALL_x_SEASONS % showtitle
        )
        for index, item in enumerate(staged_seasons):
            self.progressdialog._update(
                index / len(staged_seasons),
                '\n'.join([item.showtitle, item.episode_title_with_id])
            )
            xbmc.sleep(100)
            item.add_to_library()
        self.progressdialog._close()
        notification(STR_ALL_x_SEASONS_ADDED % showtitle)

    @logged_function
    def add_all_seasons_with_metadata(self, showtitle):
        """Add all seasons in the specified show with metadata to the library."""
        STR_ADDING_ALL_x_SEASONS_WITH_METADATA = 'Adding all %s seasons with metadata...'
        STR_ALL_x_SEASONS_WITH_METADATA_ADDED = 'All %s seasons with metadata added'
        staged_seasons = list(
            self.database.get_season_items(
                status='staged',
                showtitle=showtitle
            )
        )
        self.progressdialog._create(
            msg=STR_ADDING_ALL_x_SEASONS_WITH_METADATA % showtitle
        )
        for index, item in enumerate(staged_seasons):
            if os.path.exists(item.episode_nfo[0]):
                self.progressdialog._update(
                    index / len(staged_seasons),
                    '\n'.join([item.showtitle, item.episode_title_with_id])
                )
                item.add_to_library()
        self.progressdialog._close()
        notification(STR_ALL_x_SEASONS_WITH_METADATA_ADDED % showtitle)

    @logged_function
    def generate_all_episodes_metadata(self, items):
        """Generate metadata items for all episodes in show."""
        STR_GENERATING_ALL_x_METADATA = getlocalizedstring(32077)
        STR_ALL_x_METADATA_CREATED = getlocalizedstring(32078)
        showtitle = items[0].showtitle
        self.progressdialog._create(
            msg=STR_GENERATING_ALL_x_METADATA % showtitle
        )
        for index, item in enumerate(items):
            self.progressdialog._update(
                index / len(items),
                '\n'.join([item.showtitle, item.episode_title_with_id])
            )
            item.create_metadata_item()
        self.progressdialog._close()
        notification(STR_ALL_x_METADATA_CREATED % showtitle)

    @logged_function
    def generate_all_seasons_metadata(self, showtitle):
        """Generate metadata items for all seasons in show."""
        STR_GENERATING_ALL_x_METADATA = 'Generating all %s metadata...'
        STR_ALL_x_METADATA_CREATED = 'All %s metadata created'
        staged_seasons = list(
            self.database.get_content_items(
                status='staged',
                _type='tvshow'
            )
        )
        self.progressdialog._create(
            msg=STR_GENERATING_ALL_x_METADATA % showtitle
        )
        for index, item in enumerate(staged_seasons):
            self.progressdialog._update(
                index / len(staged_seasons),
                '\n'.join([item.showtitle, item.episode_title_with_id])
            )
            item.create_metadata_item()
        self.progressdialog._close()
        notification(STR_ALL_x_METADATA_CREATED % showtitle)

    @staticmethod
    def rename_dialog(item):
        """Prompt input for new name, and rename if non-empty string."""
        input_ret = xbmcgui.Dialog().input(
            "Title",
            defaultt=item.showtitle
        )
        if input_ret:
            item.rename(input_ret)

    @logged_function
    def rename_episodes_using_metadata(self, items):
        """Rename all episodes in show using nfo files."""
        STR_RENAMING_x_EPISODES_USING_METADATA = getlocalizedstring(32075)
        STR_x_EPISODES_RENAMED_USING_METADATA = getlocalizedstring(32076)
        showtitle = items[0].showtitle
        self.progressdialog._create(
            msg=STR_RENAMING_x_EPISODES_USING_METADATA % showtitle
        )
        for index, item in enumerate(items):
            self.progressdialog._update(
                index / len(items),
                '\n'.join([item.showtitle, item.episode_title_with_id])
            )
        self.progressdialog._close()
        notification(STR_x_EPISODES_RENAMED_USING_METADATA % showtitle)

    @logged_function
    def add_all_shows(self):
        """Add all tvshow items to library."""
        STR_ADDING_ALL_TV_SHOWS = getlocalizedstring(32059)
        STR_ALL_TV_SHOWS_ADDED = getlocalizedstring(32060)
        self.progressdialog._create(
            msg=STR_ADDING_ALL_TV_SHOWS
        )
        staged_tv_items = list(
            self.database.get_content_items(
                status='staged',
                _type='tvshow'
            )
        )
        for index, item in enumerate(staged_tv_items):
            self.progressdialog._update(
                index / len(staged_tv_items),
                '\n'.join([item.showtitle, item.episode_title_with_id])
            )
            item.add_to_library()
        self.progressdialog._close()
        notification(STR_ALL_TV_SHOWS_ADDED)

    @logged_function
    def remove_all(self):
        """Remove all staged tvshow items."""
        STR_REMOVING_ALL_TV_SHOWS = getlocalizedstring(32024)
        STR_ALL_TV_SHOW_REMOVED = getlocalizedstring(32025)
        self.progressdialog._create(
            msg=STR_REMOVING_ALL_TV_SHOWS
        )
        self.database.remove_from(
            status='staged',
            _type='tvshow'
        )
        self.progressdialog._close()
        notification(STR_ALL_TV_SHOW_REMOVED)

    @logged_function
    def remove_all_seasons(self, showtitle):
        """Remove all seasons from the specified show."""
        STR_REMOVING_ALL_x_SEASONS = getlocalizedstring(32032) % showtitle
        STR_ALL_x_SEASONS_REMOVED = getlocalizedstring(32033) % showtitle
        self.progressdialog._create(
            msg=STR_REMOVING_ALL_x_SEASONS
        )
        self.database.remove_from(
            status='staged',
            _type='tvshow',
            showtitle=showtitle
        )
        self.progressdialog._close()
        notification(STR_ALL_x_SEASONS_REMOVED)

    @logged_function
    def remove_all_episodes(self, showtitle):
        """Remove all episodes from the specified show."""
        STR_REMOVING_ALL_x_EPISODES = getlocalizedstring(32032) % showtitle
        STR_ALL_x_EPISODES_REMOVED = getlocalizedstring(32033) % showtitle
        self.progressdialog._create(
            msg=STR_REMOVING_ALL_x_EPISODES
        )
        self.database.remove_from(
            status='staged',
            _type='tvshow',
            showtitle=showtitle
        )
        self.progressdialog._close()
        notification(STR_ALL_x_EPISODES_REMOVED)

    @logged_function
    def remove_and_block_show(self, showtitle):
        """
        Remove all seasons from specified show from the library.

        Delete managed, and add to blocked list.
        """
        # Remove from staged
        self.remove_all_seasons(showtitle)
        # Delete managed folder
        # --------- >
        # TODO: Place atention in this part of code
        #   - Why delete 'clean show title'?
        #   - Is realy working?

        managed_dir = os.path.join(
            'movies',
            clean_name(showtitle)
        )
        remove_dir(managed_dir)
        # --------- >
        # Add show title to blocked
        self.database.add_blocked_item(
            showtitle,
            'tvshow'
        )

    @logged_function
    def episode_options(self, item, season):
        """Provide options for a single staged episode in a dialog window."""
        # TODO: rename associated metadata when renaming
        # TODO: rename show title
        # TODO: remove item (including metadata)
        STR_ADD = getlocalizedstring(32048)
        STR_REMOVE = getlocalizedstring(32017)
        STR_REMOVE_AND_BLOCK_EPISODE = getlocalizedstring(32079)
        STR_RENAME = getlocalizedstring(32050)
        STR_GENERATE_METADATA_ITEM = getlocalizedstring(32052)
        STR_BACK = getlocalizedstring(32011)
        STR_STAGED_EPISODE_OPTIONS = getlocalizedstring(32080)
        lines = [
            STR_ADD, STR_REMOVE,
            STR_RENAME,
            STR_GENERATE_METADATA_ITEM,
            STR_BACK
        ]
        ret = xbmcgui.Dialog().select(
            '{0} - {1} - {2}'.format(
                STR_STAGED_EPISODE_OPTIONS,
                color(item.showtitle, 'skyblue'),
                color(item.episode_title_with_id.split(
                    ' - ')[0], colorname='green')
            ), lines
        )
        if ret >= 0:
            if lines[ret] == STR_ADD:
                item.add_to_library()
                self.view_episodes(item.showtitle, season)
            elif lines[ret] == STR_REMOVE:
                item.delete()
                self.view_episodes(item.showtitle, season)
            elif lines[ret] == STR_REMOVE_AND_BLOCK_EPISODE:
                item.remove_and_block()
                self.view_episodes(item.showtitle, season)
            elif lines[ret] == STR_RENAME:
                self.rename_dialog(item)
                self.episode_options(item, season)
            elif lines[ret] == STR_GENERATE_METADATA_ITEM:
                item.create_metadata_item()
                self.episode_options(item, season)
            elif lines[ret] == STR_BACK:
                self.view_episodes(item.showtitle, season)
                return
        else:
            self.view_episodes(item.showtitle, season)

    @logged_function
    def view_episodes(self, showtitle, season):
        """
        Display all staged episodes in the specified show, which are selectable and lead to options.

        Also provides additional options at bottom of menu.
        """
        STR_NO_STAGED_x_EPISODES = getlocalizedstring(32065)
        STR_ADD_ALL_EPISODES = getlocalizedstring(32066)
        STR_REMOVE_ALL_EPISODES = getlocalizedstring(32029)
        STR_REMOVE_AND_BLOCK_TV_SHOW = getlocalizedstring(32068)
        STR_AUTOMATICALLY_RENAME_ALL_EPISODES_USING_METADATA = getlocalizedstring(
            32069)
        STR_GENERATE_ALL_METADATA_ITEMS = getlocalizedstring(32040)
        STR_BACK = getlocalizedstring(32011)
        STR_STAGED_x_EPISODES = getlocalizedstring(32070)
        staged_episodes = list(
            self.database.get_episode_items(
                status='staged',
                showtitle=showtitle,
                season=season
            )
        )
        if not staged_episodes:
            xbmcgui.Dialog().ok(
                ADDON_NAME,
                STR_NO_STAGED_x_EPISODES % color(showtitle, 'skyblue')
            )
            self.view_shows()
            return
        lines = [str(x) for x in staged_episodes]
        lines += [
            STR_ADD_ALL_EPISODES,
            STR_REMOVE_ALL_EPISODES,
            STR_REMOVE_AND_BLOCK_TV_SHOW,
            STR_AUTOMATICALLY_RENAME_ALL_EPISODES_USING_METADATA,
            STR_GENERATE_ALL_METADATA_ITEMS,
            STR_BACK
        ]
        ret = xbmcgui.Dialog().select(
            '%s - %s' % (
                ADDON_NAME,
                STR_STAGED_x_EPISODES % color(showtitle, 'skyblue')
            ), lines
        )
        if ret >= 0:
            if ret < len(staged_episodes):  # staged item
                for i, item in enumerate(staged_episodes):
                    if ret == i:
                        self.episode_options(item, season)
                        break
            elif lines[ret] == STR_ADD_ALL_EPISODES:
                self.add_all_episodes(staged_episodes)
                self.view_shows()
            elif lines[ret] == STR_REMOVE_ALL_EPISODES:
                self.remove_all_episodes(showtitle)
                self.view_shows()
            elif lines[ret] == STR_REMOVE_AND_BLOCK_TV_SHOW:
                self.remove_and_block_show(showtitle)
                self.view_shows()
            elif lines[ret] == STR_AUTOMATICALLY_RENAME_ALL_EPISODES_USING_METADATA:
                self.rename_episodes_using_metadata(staged_episodes)
                self.view_episodes(showtitle, season)
            elif lines[ret] == STR_GENERATE_ALL_METADATA_ITEMS:
                self.generate_all_episodes_metadata(staged_episodes)
                self.view_episodes(showtitle, season)
            elif lines[ret] == STR_BACK:
                self.view_seasons(showtitle)
        else:
            self.view_seasons(showtitle)

    @logged_function
    def view_seasons(self, showtitle):
        """
        Display all staged seasons in the specified show, which are selectable and lead to options.

        Also provides additional options at bottom of menu.
        """
        STR_NO_STAGED_x_SEASONS = getlocalizedstring(32170)
        STR_ADD_ALL_SEASONS = getlocalizedstring(32177)
        STR_REMOVE_ALL_SEASONS = getlocalizedstring(32171)
        STR_REMOVE_AND_BLOCK_TV_SHOW = getlocalizedstring(32068)
        STR_BACK = getlocalizedstring(32011)
        STR_STAGED_x_SEASONS = getlocalizedstring(32176)
        staged_seasons = list(
            self.database.get_season_items(
                status='staged',
                showtitle=showtitle
            )
        )
        if not staged_seasons:
            xbmcgui.Dialog().ok(
                ADDON_NAME,
                STR_NO_STAGED_x_SEASONS % color(showtitle, 'skyblue')
            )
            self.view_shows()
            return
        season_interger_list = list(set([x.season for x in staged_seasons]))
        lines = [str('[B]Season %s[/B]' % x) for x in season_interger_list]
        lines += [
            STR_ADD_ALL_SEASONS,
            STR_REMOVE_ALL_SEASONS,
            STR_REMOVE_AND_BLOCK_TV_SHOW,
            STR_BACK
        ]
        ret = xbmcgui.Dialog().select(
            '%s - %s' % (
                ADDON_NAME,
                STR_STAGED_x_SEASONS % color(showtitle, 'skyblue')
            ), lines
        )
        selection = lines[ret]
        if ret >= 0:
            if selection == STR_ADD_ALL_SEASONS:
                self.add_all_seasons(showtitle)
                self.view_shows()
            elif selection == STR_REMOVE_ALL_SEASONS:
                self.remove_all_seasons(showtitle)
                self.view_shows()
            elif selection == STR_REMOVE_AND_BLOCK_TV_SHOW:
                self.remove_and_block_show(showtitle)
                self.view_shows()
            elif selection == STR_BACK:
                self.view_shows()
            else:
                self.view_episodes(
                    showtitle,
                    season=''.join(
                        filter(
                            str.isdigit,
                            selection
                        )
                    )
                )
        else:
            self.view_shows()

    @logged_function
    def view_shows(self):
        """Display all managed tvshows, which are selectable and lead to options."""
        STR_NO_STAGED_TV_SHOWS = getlocalizedstring(32054)
        STR_STAGED_TV_SHOWS = getlocalizedstring(32058)
        STR_ADD_ALL_TV_SHOWS = getlocalizedstring(32055)
        STR_REMOVE_ALL_TV_SHOWS = getlocalizedstring(32057)
        STR_BACK = getlocalizedstring(32011)
        staged_tvshows = list(
            self.database.get_all_shows('staged')
        )
        if not staged_tvshows:
            xbmcgui.Dialog().ok(
                ADDON_NAME,
                STR_NO_STAGED_TV_SHOWS
            )
            return
        lines = [bold(x) for x in staged_tvshows]
        lines += [
            STR_ADD_ALL_TV_SHOWS,
            STR_REMOVE_ALL_TV_SHOWS,
            STR_BACK
        ]
        ret = xbmcgui.Dialog().select(
            '%s - %s' % (
                ADDON_NAME,
                STR_STAGED_TV_SHOWS
            ), lines
        )
        if ret >= 0:
            if ret < len(staged_tvshows):  # staged item
                for showtitle in staged_tvshows:
                    if staged_tvshows[ret] == showtitle:
                        self.view_seasons(showtitle)
                        break
            elif lines[ret] == STR_ADD_ALL_TV_SHOWS:
                self.add_all_shows()
            elif lines[ret] == STR_REMOVE_ALL_TV_SHOWS:
                self.remove_all()
            elif lines[ret] == STR_BACK:
                return
