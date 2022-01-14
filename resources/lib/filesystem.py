# -*- coding: utf-8 -*-
# pylint: disable=broad-except

"""Filesystem utils for Windows/Linux."""

import os

import xbmcvfs

from os.path import dirname
from os.path import basename

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
        with xbmcvfs.File(self.filepath, "w+") as nfofile:
            try:
                nfofile.write(self.root)
                log_msg(f"Created NFO file {self.root}")
            except Exception as error:
                raise f"CreateNfo.create: {error}"
            finally:
                nfofile.close()

def create_stream_file(plugin_path, filepath):
    """Create stream file with plugin_path at filepath."""
    with xbmcvfs.File(filepath, "w+") as strm:
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
    if xbmcvfs.exists(dir_path):
        return False
    return xbmcvfs.mkdirs(dir_path)


# def mv_with_type(title_path, filetype, title_dst):
#     """Move files with wildcard between title_path & filetype to title_dst."""
#     os.system('mv "{0}"*{1} "{2}{1}"'.format(title_path, filetype, title_dst))

def listdir(dir_path_to_list, full_path=False):
    """Function to list files in dir."""
    itens = []
    for item in xbmcvfs.listdir(dir_path_to_list):
        for content in item:
            if full_path:
                full_path = join([dir_path_to_list, content])
                if isdir(full_path):
                    itens.append(full_path)
                else:
                    itens.append(join([dir_path_to_list, content], True))
            else:
                itens.append(content)
    return itens

def delete_strm(path_to_remove):
    """Remove one or more strm files."""
    try:
        rm_files = [file for file in listdir(path_to_remove) if ".strm" in file]
        for file in rm_files:
            xbmcvfs.delete(file)
    except Exception:
        xbmcvfs.delete(path_to_remove)

def delete_with_wildcard(title_path):
    """Remove all files starting with title_path using wildcard."""
    wildcard = basename(title_path)
    directory = dirname(title_path)
    try:
        for file in listdir(dirname(directory)):
            if wildcard in file:
                try:
                    xbmcvfs.delete(file)
                except FileNotFoundError:
                    pass
    except Exception as err:
        raise err

def isdir(path):
    """Check if folder path is a real folder (like a os.path.isdir but with xbmcvfs)."""
    is_dir_file = os.path.join(path, "is_path.txt")
    test_path_file = xbmcvfs.File(is_dir_file, 'w').write("success")
    xbmcvfs.delete(is_dir_file)
    return test_path_file

def join(array_with_paths_parts, file=False):
    """Join like os.path.join but add \\ or / if necessary."""
    joined_path = os.path.join(*array_with_paths_parts)
    if file:
        return joined_path
    return "".join([joined_path, "\\" if os.name == "nt" else "/"])

def removedirs(base_path):
    """Complete delete a diretory and all files and subdirs."""
    dirs_to_delete = []
    for path_to_delete in listdir(base_path, True):
        # Delete a file
        xbmcvfs.delete(path_to_delete)

        # Delete a dir
        dirs_to_delete.append(path_to_delete)
        if isdir(path_to_delete):
            removedirs(path_to_delete)

    for diretory in dirs_to_delete:
        removedir(diretory)
    removedir(base_path)

def removedir(dir_path):
    """Remove directory at dir_path."""
    if os.name == 'nt':
        if not dir_path.endswith("\\"):
            dir_path = dir_path + "\\"
    else:
        if not dir_path.endswith("/"):
            dir_path = dir_path + "/"

    xbmcvfs.rmdir(dir_path, True)
