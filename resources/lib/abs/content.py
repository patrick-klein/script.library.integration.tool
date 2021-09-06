# -*- coding: utf-8 -*-

"""Module with abs content classes."""

from abc import ABCMeta
from abc import abstractmethod
from abc import abstractproperty


class ABSContentManagerShow():
    """Abstract base class for ContentManager."""

    __metaclass__ = ABCMeta
    # TODO: Make rename on add optional in settings
    # TODO: Save original_label, would be able to rename
    # entire filename using metadata

    def __init__(self, _):
        """__init__ ABSContentManagerShow."""

    def __str__(self):
        """Return str title formated with file path."""
        return '[B]%s[/B] - [I]%s[/I]' % (
            self.episode_title_with_id,
            self.file
        )

    @property
    @abstractproperty
    def showtitle(self):
        """Return showtitle str."""

    @property
    @abstractproperty
    def season(self):
        """Return season as interger"""

    @property
    @abstractproperty
    def show_dir(self):
        """Return show_dir path."""

    @property
    @abstractproperty
    def formedyear(self):
        """Return formedyear str."""

    @property
    @abstractproperty
    def complete_episode_title(self):
        """Return complete_episode_title str."""

    @property
    @abstractproperty
    def file(self):
        """Return file (stream link) str."""

    @property
    @abstractproperty
    def episode_title_with_id(self):
        """Return episode_title_with_id str."""

    @property
    @abstractproperty
    def episode_id(self):
        """Return episode_id str."""

    @abstractmethod
    def add_to_library(self):
        """Add content to the library."""
        # TODO: add to library using json-rpc

    @abstractmethod
    def remove_from_library(self):
        """Remove its content from the library, does NOT change/remove item in database."""
        # TODO: remove from library using json-rpc

    @abstractmethod
    def remove_and_block(self):
        """Remove content from the library, deletes metadata, and adds to blocked list."""

    @abstractmethod
    def create_metadata_item(self):
        """Add relevent files to metadata folder."""

    # @abstractmethod
    # def rename(self, name):
    #     """Rename title and files."""

    @abstractmethod
    def delete(self):
        """Remove the item from the database."""

    @abstractmethod
    def set_as_staged(self):
        """Set the item status as staged in database."""


class ABSContentManagerMovie():
    """
    Abstract base class for ContentManager.

    Defines required and helper methods.
    """

    __metaclass__ = ABCMeta
    # TODO: Make rename on add optional in settings
    # TODO: Save original_label, would be able to rename entire filename using metadata

    def __init__(self, _):
        """__init__ ABSContentManagerMovie."""

    def __str__(self):
        """Return str title formated with file path."""
        return '[B]%s[/B] - [I]%s[/I]' % (
            self.title,
            self.file
        )

    @property
    @abstractproperty
    def file(self):
        """Return episode_title_with_id str."""

    @property
    @abstractproperty
    def title(self):
        """Return title str."""

    @property
    @abstractproperty
    def year(self):
        """Return year str."""

    @property
    @abstractproperty
    def formedyear(self):
        """Return formedyear str."""

    @property
    @abstractproperty
    def movie_dir(self):
        """Return movie_dir str."""

    @property
    @abstractproperty
    def movie_nfo(self):
        """Return movie_nfo str."""

    @abstractmethod
    def add_to_library(self):
        """Add content to the library."""
        # TODO: add to library using json-rpc

    @abstractmethod
    def remove_from_library(self):
        """Remove its content from the library, does NOT change/remove item in database."""
        # TODO: remove from library using json-rpc

    @abstractmethod
    def remove_and_block(self):
        """Remove content from the library, deletes metadata, and adds to blocked list."""

    @abstractmethod
    def create_metadata_item(self):
        """Add relevent files to metadata folder."""

    @abstractmethod
    def rename(self, name):
        """Rename title and files."""

    @abstractmethod
    def delete(self):
        """Remove the item from the database."""

    @abstractmethod
    def set_as_staged(self):
        """Set the item status as staged in database."""
