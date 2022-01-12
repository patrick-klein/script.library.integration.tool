# -*- coding: utf-8 -*-
# pylint: disable=broad-except

"""Filesystem utils for Windows/Linux."""

import os
from os import remove

from pathlib import Path
from shutil import rmtree

from os.path import dirname
from os.path import basename

from os.path import isdir
from os.path import isfile
from os.path import exists

from resources.lib.log import log_msg


class CreateNfo():
    """
    Module to create a .nfo file.

    Future possible new keys:
        title, showtitle, year, runtime, thumb aspect="poster"
        thumb aspect="poster" season="1" type="season", id, imdbid.
    """

    def __init__(self, _type, filepath, jsondata):
        """__init__ CreateNfo."""
        self.type = _type
        self.filepath = filepath
        self.jsondata = jsondata
        ROOT_TYPES = {
            'tvshow': '<tvshow>\n%s</tvshow>',
            'episodedetails': '<episodedetails>\n%s</episodedetails>',
            'movie': '<movie>\n%s</movie>',
        }
        self.root = ''.join(
            [
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n',
                ROOT_TYPES[self.type]
            ]
        )

        self.create()

    def tvshow(self):
        """Create tvshow nfo file."""
        if self.type == 'tvshow':
            return ''.join(
                [
                    '\t<title>{showtitle}</title>\n',
                    '\t<showtitle>{showtitle}</showtitle>\n',
                    '\t<year>{year}</year>\n'
                ]
            ).format(**self.jsondata)

    def episodedetails(self):
        """
        Create episodedetails nfo for tvshow.

        Future possible new keys:
            id, uniqueid default="true" type="tvdb", runtime, thumb.
        """
        if self.type == 'episodedetails':
            return ''.join(
                [
                    '\t<title>{title}</title>\n',
                    '\t<showtitle>{showtitle}</showtitle>\n',
                    '\t<season>{season}</season>\n',
                    '\t<episode>{episode}</episode_number>\n',
                    '\t<year>{year}</year>\n',
                    '\t<original_filename>{file}</original_filename>\n'
                ]
            ).format(**self.jsondata)

    def movie(self):
        """
        Create movie nfo.

        future possible new keys:
            runtime, thumb aspect="poster", fanart, thumb, id, tmdbid.
        """
        if self.type == 'movie':
            return ''.join(
                [
                    '\t<title>{title}</title>\n',
                    '\t<year>{year}</year>\n',
                    '\t<original_filename>{file}</original_filename>\n'
                ]
            ).format(**self.jsondata)

    def create(self):
        """
        Create the nfo file.

        element root: movie, tvshow or episodedetails
        tvshow            title, showtitle
        movie             title
        episodedetails    title, showtitle.
        """
        body = self.tvshow() or self.episodedetails() or self.movie()
        self.root = self.root % body
        with open(self.filepath, "w+") as nfofile:
            try:
                nfofile.write(self.root)
                log_msg(f"Created NFO file {self.root}")
            except Exception as error:
                raise f"CreateNfo.create: {error}"
            finally:
                nfofile.close()

def create_stream_file(plugin_path, filepath):
    """Create stream file with plugin_path at filepath."""
    with open(filepath, "w+") as strm:
        try:
            strm.write(plugin_path)
            log_msg(f"Created STRM file {plugin_path}")
        except Exception as error:
            raise f"filesystem.create_stream_file: {error}"
        finally:
            strm.close()
    return True


def mkdir(dir_path):
    """Create a directory."""
    try:
        Path(dir_path).mkdir(
            mode=0o755,
            parents=True,
            exist_ok=True
        )
    except Exception as error:
        log_msg('filesystem.mkdir: %s' % error)
    return True

# def mv_with_type(title_path, filetype, title_dst):
#     """Move files with wildcard between title_path & filetype to title_dst."""
#     os.system('mv "{0}"*{1} "{2}{1}"'.format(title_path, filetype, title_dst))


def delete_strm(path_to_remove):
    """Remove one or more strm files."""
    if isdir(path_to_remove):
        rm_files = [
            strm_file for strm_file in os.listdir(
                path_to_remove
            ) if ".strm" in strm_file
        ]
        for file in rm_files:
            remove(file)
    elif isfile(path_to_remove):
        remove(path_to_remove)


def delete_with_wildcard(title_path):
    """Remove all files starting with title_path using wildcard."""
    wildcard = basename(title_path)
    directory = dirname(title_path)
    if exists(directory):
        for file in os.listdir(dirname(directory)):
            if wildcard in file:
                try:
                    os.remove(file, dir_fd=None)
                except FileNotFoundError:
                    pass


def remove_dir(dir_path):
    """Remove directory at dir_path."""
    try:
        rmtree(dir_path, ignore_errors=False, onerror=None)
    except FileNotFoundError:
        pass
