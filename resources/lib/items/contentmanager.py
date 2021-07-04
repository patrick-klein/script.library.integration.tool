#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Defines the ContentManagerShow class."""

from os import listdir
from os.path import join
from os.path import isdir
from os.path import exists
from os.path import splitext

# from resources import USE_SHOW_ARTWORK
from resources.lib.log import logged_function

from resources.lib.filesystem import mkdir
from resources.lib.filesystem import CreateNfo
from resources.lib.filesystem import remove_dir
from resources.lib.filesystem import create_stream_file
from resources.lib.filesystem import delete_with_wildcard

from resources.lib.abs.content import ABSContentManagerShow
from resources.lib.abs.content import ABSContentManagerMovie


class ContentManagerShow(ABSContentManagerShow):
    """Class with methods to manage a show item."""

    def __init__(self, database, jsondata):
        """__init__ ContentManagerShow."""
        super(ContentManagerShow, self).__init__(jsondata)
        self.database = database
        # This regex has the function of detecting the patterns detected by the kodi
        # https://kodi.wiki/view/Naming_video_files/TV_shows
        self.jsondata = jsondata
        self.managed_season_dir = join(
            self.show_dir, self.jsondata['season_dir'])
        self.managed_episode_path = join(
            self.managed_season_dir, self.complete_episode_title)
        self.managed_thumb_path = ''.join(
            [self.managed_episode_path, '-thumb.jpg'])
        self.managed_landscape_path = join(self.show_dir, 'landscape.jpg')
        self.managed_tvshow_nfo = join(self.show_dir, 'tvshow.nfo')
        self.managed_strm_path = ''.join([self.managed_episode_path, '.strm'])

    @property
    def showtitle(self):
        """Return showtitle."""
        return self.jsondata['showtitle']

    @property
    def season(self):
        """Return season."""
        return int(self.jsondata['season'])

    @property
    def show_dir(self):
        """Return show_dir."""
        return ' '.join(
            [self.jsondata['managed_show_dir'], self.formedyear]
        )

    @property
    def formedyear(self):
        """Return formedyear."""
        return '(%s)' % self.jsondata['year']

    @property
    def complete_episode_title(self):
        """Return complete_episode_title."""
        return '%s - %s' % (
            ' '.join([self.showtitle, self.formedyear]),
            self.episode_title_with_id
        )

    @property
    def file(self):
        """Return file."""
        return self.jsondata['file']

    @property
    def episode_title_with_id(self):
        """Return episode_title_with_id."""
        return self.jsondata['episode_title_with_id']

    @property
    def managed_episode_nfo_path(self):
        """Return managed_episode_nfo_path."""
        return ''.join([self.managed_episode_path, '.nfo'])

    @logged_function
    def add_to_library(self):
        """Add item to library."""
        # Create show_dir (tv show folder) in managed/tvshow/ diretory
        mkdir(self.show_dir)
        # Create season_dir (tv show season folder) in managed/tvshow/show_dir/
        mkdir(self.managed_season_dir)
        # Create stream file
        if create_stream_file(self.file, self.managed_strm_path):
            # self.create_metadata_item()
            self.database.update_content(
                file=self.file,
                status='managed',
                _type='tvshow'
            )
        return True

    @logged_function
    # TODO: maybe this method is not necessay
    # whem item is added from staged, the nfo and strm will be created
    def add_to_library_if_metadata(self):
        # """Add to library with metadata."""
        if exists(self.managed_episode_nfo_path):
            self.add_to_library()

    @logged_function
    def create_metadata_item(self):
        """Create metadata."""
        # Create show_dir (tv show folder) in managed/tvshow/ diretory
        mkdir(self.show_dir)
        # Create tvshow.nfo in managed/tvshow
        CreateNfo(
            _type='tvshow',
            filepath=self.managed_tvshow_nfo,
            jsondata=self.jsondata
        )
        # Create a episode nfo in managed/tvshow/show_dir/Season X
        CreateNfo(
            _type='episodedetails',
            filepath=self.managed_episode_nfo_path,
            jsondata=self.jsondata
        )
        # # Link metadata for episode if it exists
        # if USE_SHOW_ARTWORK:
        #     # Try show landscape or fanart (since Kodi can't generate thumb for strm)
        #     if exists(self.metadata_landscape_path):
        #         softlink_file(
        #             self.metadata_landscape_path,
        #             self.managed_landscape_path
        #         )
        #     elif exists(self.metadata_fanart_path):
        #         softlink_file(
        #             self.metadata_fanart_path,
        #             self.metadata_fanart_path
        #         )
        self.database.update_content(
            self.file,
            title=self.jsondata['title'],
            _type='tvshow'
        )

    @logged_function
    def remove_and_block(self):
        """Remove item from library and block."""
        # TODO: Need to remove nfo for all other items that match blocked
        # Add episode title to blocked
        self.database.add_blocked_item(
            self.showtitle,
            'episode'
        )
        # Delete nfo items
        delete_with_wildcard(splitext(self.managed_episode_nfo_path)[0])
        # Remove from db
        self.database.remove_from(
            file=self.file,
            _type='episode'
        )

    @logged_function
    def remove_from_library(self):
        """Remove from library."""
        # Delete stream & episode nfo
        delete_with_wildcard(self.managed_strm_path)
        # Check if last stream file, and remove entire dir if so
        if isdir(self.show_dir):
            files = listdir(self.show_dir)
            for fname in files:
                if '.strm' in fname:
                    break
            else:
                remove_dir(self.show_dir)

    # TODO: in future, rename can be usefull to rename showtitle and title (episode_title),
    # store a table with file, original_title and newtitle can be a more easily way to performe this

    # @logged_function
    # def rename(self, name):
    #     # Rename files if they exist
    #     # TODO: I supose this function is working, but not change the name,
    #     # becouse the new_title is equal the original
    #     if exists(self.show_dir):
    #         # Define "title paths" (paths without extensions)
    #         title_path = join(self.show_dir, self.showtitle)
    #         new_title_path = join(self.show_dir, self.showtitle)
    #         # Rename stream placeholder, nfo file, and thumb
    #         mv_with_type(title_path, '.strm', new_title_path)
    #         mv_with_type(title_path, '.nfo', new_title_path)
    #         mv_with_type(title_path, '-thumb.jpg', new_title_path)
    #     # Rename property and refresh in staged file
    #     # TODO: self.showtitle here is the global self.showtitle
    #     # in future, the value need be updated to a new diferente formed name
    #     resources.lib.database.DatabaseHandler().update_content(
    #         self.file,
    #         title=self.showtitle,
    #         _type='tvshow'
    #     )

    def delete(self):
        """Remove the item from the database."""
        self.database.remove_from(
            _type='tvshow',
            file=self.file
        )

    def set_as_staged(self):
        """Set the item status as staged in database."""
        self.database.update_content(
            file=self.file,
            status='staged',
            _type='tvshow'
        )


class ContentManagerMovie(ABSContentManagerMovie):
    """Class with methods to manage a show item."""

    def __init__(self, database, jsondata):
        """__init__ ContentManagerMovie."""
        super(ContentManagerMovie, self).__init__(jsondata)
        self.database = database
        self.jsondata = jsondata
        self.managed_strm_path = join(
            self.managed_movie_dir,
            ''.join([self.title, '.strm'])
        )

    @property
    def file(self):
        """Return file."""
        return self.jsondata['file']

    @property
    def title(self):
        """Return title."""
        return ' '.join([self.jsondata['title'], self.formedyear])

    @property
    def year(self):
        """Return year."""
        return self.jsondata['year']

    @property
    def formedyear(self):
        """Return formedyear."""
        return '(%s)' % self.jsondata['year']

    @property

    def managed_movie_dir(self):
        """Return managed_movie_dir."""
        return ' '.join([self.jsondata['managed_movie_dir'], self.formedyear])

    @property
    def movie_nfo(self):
        """Return movie_nfo."""
        return join(self.managed_movie_dir, ''.join([self.title, '.nfo']))

    @logged_function
    def add_to_library(self):
        """Add item to library."""
        # Create managed_movie_dir (movie folder) in managed/movies/ diretory
        mkdir(self.managed_movie_dir)
        # Create stream_file in managed/movies/managed_movie_dir
        self.create_metadata_item()
        create_stream_file(
            self.file,
            self.managed_strm_path
        )
        self.database.update_content(
            file=self.file,
            status='managed',
            _type='movie'
        )

    @logged_function
    def create_metadata_item(self):
        """Create metadata movie item."""
        # Create managed_movie_dir (movie folder) in managed/movies/ diretory
        mkdir(self.managed_movie_dir)
        CreateNfo(
            _type='movie',
            filepath=self.movie_nfo,
            jsondata=self.jsondata
        )

        self.database.update_content(
            file=self.file,
            _type='movie',
            title=self.jsondata['title'],
        )

    @logged_function
    # TODO: maybe this method is not necessay
    # whem item is added from staged, the nfo and strm will be created
    def add_to_library_if_metadata(self):
        # """Add item to library with metadata."""
        if exists(self.movie_nfo):
            self.add_to_library()

    @logged_function
    def remove_and_block(self):
        """Remove item and block."""
        # Add title to blocked
        self.database.add_blocked_item(
            self.title,
            'movie'
        )
        # Delete metadata items
        remove_dir(self.managed_movie_dir)
        # Remove from db
        self.database.remove_from(
            file=self.file,
            _type='movie'
        )

    @logged_function
    def remove_from_library(self):
        """Remove from library."""

    def rename(self, name):
        """Rename item."""
        # TODO: Implement
        raise NotImplementedError('contentitem.rename(name) not implemented!')

    def rename_using_metadata(self):
        # """Rename item using metadata."""
        # TODO: Implement
        raise NotImplementedError('contentitem.rename(name) not implemented!')

    def delete(self):
        """Remove the item from the database."""
        self.database.remove_from(
            _type='movie',
            file=self.file
        )

    def set_as_staged(self):
        """Set the item status as staged in database."""
        self.database.update_content(
            file=self.file,
            status='staged',
            _type='movie'
        )
