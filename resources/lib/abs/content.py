#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Module with abs content classes."""

import abc


class ABSContentManagerShow(object):
    """Abstract base class for ContentManager."""

    __metaclass__ = abc.ABCMeta
    # TODO: Make rename on add optional in settings
    # TODO: Save original_label, would be able to rename
    # entire filename using metadata

    def __init__(self, jsondata):
        """__init__ ABSContentManagerShow."""
        self._file = None
        self._title = None
        self._showtitle = None
        self._season = None
        self._episode = None
        self._year = None

    def __str__(self):
        """Return str title formated with file path."""
        return '[B]%s[/B] - [I]%s[/I]' % (
            self.episode_title_with_id,
            self.file
        )

    @abc.abstractproperty
    def showtitle(self):
        """Return showtitle str."""

    @abc.abstractproperty
    def season(self):
        """Return season as interger"""

    @abc.abstractproperty
    def show_dir(self):
        """Return show_dir path."""

    @abc.abstractproperty
    def formedyear(self):
        """Return formedyear str."""

    @abc.abstractproperty
    def complete_episode_title(self):
        """Return complete_episode_title str."""

    @abc.abstractproperty
    def file(self):
        """Return file (stream link) str."""

    @abc.abstractproperty
    def episode_title_with_id(self):
        """Return episode_title_with_id str."""

    @abc.abstractproperty
    def episode_id(self):
        """Return episode_id str."""

    @abc.abstractproperty
    def episode_nfo(self):
        """Return episode_nfo str."""

    @abc.abstractmethod
    def add_to_library(self):
        """Add content to the library."""
        # TODO: add to library using json-rpc

    @abc.abstractmethod
    def remove_from_library(self):
        """Remove its content from the library, does NOT change/remove item in database."""
        # TODO: remove from library using json-rpc

    @abc.abstractmethod
    def remove_and_block(self):
        """Remove content from the library, deletes metadata, and adds to blocked list."""

    @abc.abstractmethod
    def create_metadata_item(self):
        """Add relevent files to metadata folder."""

    @abc.abstractmethod
    def rename(self, name):
        """Rename title and files."""

    @abc.abstractmethod
    def delete(self):
        """Remove the item from the database."""

    @abc.abstractmethod
    def set_as_staged(self):
        """Set the item status as staged in database."""


class ABSContentManagerMovie(object):
    """
    Abstract base class for ContentManager.

    Defines required and helper methods.
    """

    __metaclass__ = abc.ABCMeta
    # TODO: Make rename on add optional in settings
    # TODO: Save original_label, would be able to rename entire filename using metadata

    def __init__(self, jsondata):
        """__init__ ABSContentManagerMovie."""
        self._file = None
        # type
        self._title = None
        self._year = None

    def __str__(self):
        """Return str title formated with file path."""
        return '[B]%s[/B] - [I]%s[/I]' % (
            self.title,
            self.file
        )

    @abc.abstractproperty
    def file(self):
        """Return episode_title_with_id str."""

    @abc.abstractproperty
    def title(self):
        """Return title str."""

    @abc.abstractproperty
    def year(self):
        """Return year str."""

    @abc.abstractproperty
    def formedyear(self):
        """Return formedyear str."""

    @abc.abstractproperty
    def movie_dir(self):
        """Return movie_dir str."""

    @abc.abstractproperty
    def movie_nfo(self):
        """Return movie_nfo str."""

    @abc.abstractmethod
    def add_to_library(self):
        """Add content to the library."""
        # TODO: add to library using json-rpc

    @abc.abstractmethod
    def remove_from_library(self):
        """Remove its content from the library, does NOT change/remove item in database."""
        # TODO: remove from library using json-rpc

    @abc.abstractmethod
    def remove_and_block(self):
        """Remove content from the library, deletes metadata, and adds to blocked list."""

    @abc.abstractmethod
    def create_metadata_item(self):
        """Add relevent files to metadata folder."""

    @abc.abstractmethod
    def rename(self, name):
        """Rename title and files."""

    @abc.abstractmethod
    def delete(self):
        """Remove the item from the database."""

    @abc.abstractmethod
    def set_as_staged(self):
        """Set the item status as staged in database."""
