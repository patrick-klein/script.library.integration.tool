# -*- coding: utf-8 -*-

"""Defines the ContentManagerShow class."""

from os.path import splitext
from resources import AUTO_CREATE_NFO_SHOWS
from resources import AUTO_CREATE_NFO_MOVIES

# from resources import USE_SHOW_ARTWORK_SHOW
from resources.lib.log import log_msg, logged_function

from resources.lib.filesystem import join, mkdir, removedirs
from resources.lib.filesystem import CreateNfo
from resources.lib.filesystem import removedir
from resources.lib.filesystem import create_stream_file
from resources.lib.filesystem import delete_with_wildcard


class ContentManagerShow():
    """Class with methods to manage a show item."""

    def __init__(self, database, jsondata):
        """__init__ ContentManagerShow."""
        self.database = database
        # This regex has the function of detecting the patterns detected by the kodi
        # https://kodi.wiki/view/Naming_video_files/TV_shows
        self.jsondata = jsondata
        self.managed_season_dir = join([
            self.show_dir(),
            self.jsondata['season_dir']
        ])
        self.managed_episode_path = join([
            self.managed_season_dir,
            self.complete_episode_title()
            ],
            True
        )
        self.managed_thumb_path = f'{self.managed_episode_path}-thumb.jpg'
        self.managed_landscape_path = join([
            self.show_dir(),
            'landscape.jpg'
            ],
            True
        )
        self.managed_tvshow_nfo = join([
            self.show_dir(),
            'tvshow.nfo'
            ],
            True
        )
        self.managed_strm_path = f'{self.managed_episode_path}.strm'

    def __str__(self):
        """Return str title formated with file path."""
        return f"[B]{self.episode_title_with_id()}[/B] - [I]{self.file()}[/I]"

    def showtitle(self):
        """Return showtitle."""
        return self.jsondata['showtitle']

    def season(self):
        """Return season."""
        return int(self.jsondata['season'])

    def show_dir(self):
        """Return show_dir."""
        return f"{self.jsondata['managed_show_dir']} {self.formedyear()}"

    def formedyear(self):
        """Return formedyear."""
        return f'({self.jsondata["year"]})'

    def complete_episode_title(self):
        """Return complete_episode_title."""
        return f"{self.showtitle()} {self.formedyear()} - {self.episode_title_with_id()}"

    def file(self):
        """Return file."""
        return self.jsondata['file']

    def episode_title_with_id(self):
        """Return episode_title_with_id."""
        return self.jsondata['episode_title_with_id']

    def episode_id(self):
        """Return episode_id."""
        return self.jsondata['episode_id']

    def managed_episode_nfo_path(self):
        """Return managed_episode_nfo_path."""
        return f'{self.managed_episode_path}.nfo'

    @logged_function
    def add_to_library(self):
        """Add item to library."""
        # Create show_dir (tv show folder) in managed/tvshow/ diretory
        mkdir(self.show_dir())
        # Create season_dir (tv show season folder) in managed/tvshow/show_dir/
        mkdir(self.managed_season_dir)
        # Create stream file
        create_stream_file(self.file(), self.managed_strm_path)
        if AUTO_CREATE_NFO_MOVIES:
            self.create_metadata_item()
        if AUTO_CREATE_NFO_SHOWS:
            self.create_metadata_item()
        self.database.update_status_in_database(
            file=self.file(),
            _type='tvshow',
            status='managed'
        )
        return True

    @logged_function
    def create_metadata_item(self):
        """Create metadata."""
        # Create show_dir (tv show folder) in managed/tvshow/ diretory
        mkdir(self.show_dir())
        # Create tvshow.nfo in managed/tvshow
        CreateNfo(
            _type='tvshow',
            filepath=self.managed_tvshow_nfo,
            jsondata=self.jsondata
        )
        mkdir(self.managed_season_dir)
        # Create a episode nfo in managed/tvshow/show_dir/Season X
        CreateNfo(
            _type='episodedetails',
            filepath=self.managed_episode_nfo_path(),
            jsondata=self.jsondata
        )
        self.database.update_title_in_database(
            file=self.file(),
            _type='tvshow',
            title=self.jsondata['title']
        )

    @logged_function
    def remove_and_block(self):
        """Remove item from library and block."""
        # TODO: Need to remove nfo for all other items that match blocked
        # Add episode title to blocked
        self.database.add_blocked_item(
            self.showtitle(),
            'episode'
        )
        # Delete nfo items
        delete_with_wildcard(splitext(self.managed_episode_nfo_path())[0])
        # Remove from db
        self.database.delete_item_from_table(
            file=self.file(),
            _type='tvshow'
        )

    @logged_function
    def remove_from_library(self):
        """Delete the show_dir directory and all its contents"""
        removedirs(self.show_dir())

    # TODO: in future, rename can be usefull to rename showtitle and title (episode_title),
    # store a table with file, original_title and newtitle can be a more easily way to performe this

    # @logged_function
    # def rename(self, name):
    #     # Rename files if they exist
    #     # TODO: I supose this function is working, but not change the name,
    #     # becouse the new_title is equal the original
    #     if exists(self.show_dir()):
    #         # Define "title paths" (paths without extensions)
    #         title_path = join([self.show_dir(), self.showtitle()])
    #         new_title_path = join([self.show_dir(), self.showtitle()])
    #         # Rename stream placeholder, nfo file, and thumb
    #         mv_with_type(title_path, '.strm', new_title_path)
    #         mv_with_type(title_path, '.nfo', new_title_path)
    #         mv_with_type(title_path, '-thumb.jpg', new_title_path)
    #     # Rename property and refresh in staged file
    #     # TODO: self.showtitle() here is the global self.showtitle()
    #     # in future, the value need be updated to a new diferente formed name
    #     resources.lib.database.DatabaseHandler().update_content(
    #         self.file(),
    #         title=self.showtitle(),
    #         _type='tvshow'
    #     )

    def delete(self):
        """Remove the item from the database."""
        self.database.delete_item_from_table(
            file=self.file(),
            _type='tvshow'
        )

    def set_as_staged(self):
        """Set the item status as staged in database."""
        self.database.update_status_in_database(
            file=self.file(),
            _type='tvshow',
            status='staged'
        )


class ContentManagerMovie():
    """Class with methods to manage a show item."""

    def __init__(self, database, jsondata):
        """__init__ ContentManagerMovie."""
        self.database = database
        self.jsondata = jsondata
        self.managed_strm_path = join(
            [self.managed_movie_dir(), f'{self.title()}.strm'],
            True
        )
        log_msg(f'self.managed_strm_path {self.managed_strm_path}')

    def __str__(self):
        """Return str title formated with file path."""
        return f'[B]{self.title()}[/B] - [I]{self.file()}[/I]'

    def file(self):
        """Return file."""
        return self.jsondata['file']

    def title(self):
        """Return title."""
        return f'{self.jsondata["title"]} {self.formedyear()}'

    def year(self):
        """Return year."""
        return self.jsondata['year']

    def formedyear(self):
        """Return formedyear."""
        return f'({self.jsondata["year"]})'

    def managed_movie_dir(self):
        """Return managed_movie_dir."""
        return f'{self.jsondata["managed_movie_dir"]} {self.formedyear()}'

    def movie_nfo(self):
        """Return movie_nfo."""
        return join([self.managed_movie_dir(), f"{self.title()}.nfo"], True)

    @logged_function
    def add_to_library(self):
        """Add item to library."""
        # Create movie_dir (movie folder) in managed/movies/ diretory
        mkdir(self.managed_movie_dir())
        # Create stream_file in managed/movies/movie_dir
        self.create_metadata_item()
        create_stream_file(
            self.file(),
            self.managed_strm_path
        )
        self.database.update_status_in_database(
            file=self.file(),
            _type='movie',
            status='managed'
        )

    @logged_function
    def create_metadata_item(self):
        """Create metadata movie item."""
        # Create movie_dir (movie folder) in managed/movies/ diretory
        mkdir(self.managed_movie_dir())
        CreateNfo(
            _type='movie',
            filepath=self.movie_nfo(),
            jsondata=self.jsondata
        )

        self.database.update_title_in_database(
            file=self.file(),
            _type='movie',
            title=self.jsondata['title']
        )

    @logged_function
    def remove_and_block(self):
        """Remove item and block."""
        # Add title to blocked
        self.database.add_blocked_item(
            self.title(),
            'movie'
        )
        # Delete metadata items
        removedir(self.managed_movie_dir())
        # Remove from db
        self.database.delete_item_from_table(
            file=self.file(),
            _type='movie'
        )

    @logged_function
    def remove_from_library(self):
        """Remove from library."""
        removedirs(self.managed_movie_dir())

    def rename(self, name):
        """Rename item."""
        # TODO: Implement
        raise NotImplementedError('contentitem.rename(name) not implemented!')

    def rename_using_metadata(self):
        """Rename item using metadata."""
        # TODO: Implement
        raise NotImplementedError('contentitem.rename(name) not implemented!')

    def delete(self):
        """Remove the item from the database."""
        self.database.delete_item_from_table(
            file=self.file(),
            _type='movie'
        )

    def set_as_staged(self):
        """Set the item status as staged in database."""
        self.database.update_status_in_database(
            file=self.file(),
            _type='movie',
            status='staged'
        )
