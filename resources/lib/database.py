#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Defines the DatabaseHandler class."""

import sqlite3

from os.path import join

from resources import AUTO_ADD_MOVIES
from resources import AUTO_ADD_TVSHOWS

from resources.lib import build_json_item
from resources.lib import build_contentitem
from resources.lib import build_contentmanager

from resources.lib.log import logged_function

from resources.lib.utils import MANAGED_FOLDER

from resources.lib.items.blocked import BlockedItem
from resources.lib.items.synced import SyncedItem


class Database(object):
    """Database class with all database methods."""

    # TODO: Reimplement blocked keywords
    # TODO: Combine remove_content_item functions using **kwargs
    def __init__(self):
        """__init__ database."""
        # Connect to database
        self.conn = sqlite3.connect(join(MANAGED_FOLDER, 'managed.db'))
        self.conn.text_factory = str
        self.cur = self.conn.cursor()
        self.DELETE_DICT_QUERY = {
            "movie": "DELETE FROM movie",
            "tvshow": "DELETE FROM tvshow",
            "music": "DELETE FROM music",
        }
        # Create tables if they doesn't exist
        self.cur.execute(
            '''CREATE TABLE IF NOT EXISTS movie
            (
                file TEXT PRIMARY KEY,
                title TEXT,
                type TEXT,
                status TEXT,
                year TEXT
            )'''
        )

        self.cur.execute(
            '''CREATE TABLE IF NOT EXISTS tvshow
            (
                file TEXT PRIMARY KEY,
                title TEXT,
                type TEXT,
                status TEXT,
                year TEXT,
                showtitle TEXT,
                season TEXT,
                episode TEXT
            )'''
        )
        # FUTURE: Add a music table, for stage and add musics
        self.cur.execute(
            '''CREATE TABLE IF NOT EXISTS synced
            (
                file TEXT PRIMARY KEY,
                label TEXT,
                type TEXT
            )'''
        )
        self.cur.execute(
            '''CREATE TABLE IF NOT EXISTS blocked
            (
                value TEXT NOT NULL,
                type TEXT NOT NULL
            )'''
        )
        self.conn.commit()

    def __del__(self):
        """Close database connection."""
        self.conn.close()

    @logged_function
    def add_blocked_item(self, value, _type):
        """Add an item to blocked with the specified values."""
        # Ignore if already in table
        if not self.check_blocked(value, _type):
            self.cur.execute(
                "INSERT INTO blocked (value, type) VALUES (?, ?)", (value, _type))
            self.conn.commit()

    @logged_function
    def add_content_item(self, jsondata):
        """Add content to library."""
        sql_comm = '''
            INSERT OR IGNORE INTO
                {table}
                %s
            VALUES
                %s'''.format(table=jsondata['type'])
        query_defs = {
            'tvshow': (
                '''(file,title,type,status,year,showtitle,season,episode)''',
                '''(:file,:title,:type,'staged',:year,:showtitle,:season,:episode)'''
            ),
            'movie': (
                '''(file,title,type,status,year)''',
                '''(:file,:title,:type,'staged',:year)'''
            ),
            'music': ValueError("Not implemented yet, music")
        }[jsondata['type']]
        # sqlite named style:
        self.cur.execute(sql_comm % query_defs, jsondata)
        self.conn.commit()
        contentmanager = build_contentmanager(
            self,
            jsondata
        )
        if jsondata['type'] == 'tvshow':
            if AUTO_ADD_TVSHOWS:
                contentmanager.add_to_library()
        elif jsondata['type'] == 'movie':
            if AUTO_ADD_MOVIES:
                contentmanager.add_to_library()
        elif jsondata['type'] == 'music':
            # TODO: Music params
            raise NotImplementedError(
                'Not implemented yet'
            )

    @logged_function
    def add_synced_dir(self, label, path, _type):
        """Create an entry in synced with specified values."""
        self.cur.execute(
            '''INSERT OR REPLACE INTO
                    synced(file, label, type)
                VALUES
                    (?, ?, ?)''', (path, label, _type)
        )
        self.conn.commit()

    @logged_function
    def check_blocked(self, value, _type):
        """Return True if the given entry is in blocked."""
        # TODO: test if fetchone ir realy working
        self.cur.execute('''SELECT
                               (value)
                            FROM
                                blocked
                            WHERE
                                value=?
                            AND
                                type=?''', (value, _type))
        return bool(self.cur.fetchone())

    @logged_function
    def get_all_shows(self, status):
        """Query Content table for all (not null) distinct showtitles and cast results as list of strings."""
        # Query database
        self.cur.execute(
            '''
            SELECT DISTINCT
                showtitle
            FROM
                tvshow
            WHERE
                status=?
            ORDER BY
                (
                    CASE WHEN
                        showtitle
                    LIKE
                        'the %'
                    THEN
                        substr(showtitle,5)
                    ELSE
                        showtitle
                    END
                ) COLLATE NOCASE''', (status, )
        )
        for item in self.cur.fetchall():
            yield item[0]

    @logged_function
    def get_blocked_items(self):
        """Return all items in blocked as a list of BlockedItem objects."""
        self.cur.execute(
            '''SELECT
                    *
                FROM
                    blocked
                ORDER BY
                    type,
                    value'''
        )
        return [BlockedItem(*x) for x in self.cur.fetchall()]

    @logged_function
    def get_content_items(self, status=None, _type=None):
        """
        Query Content table for sorted items with given constaints and casts results as contentitem subclasses.

            keyword arguments:
                status: string, 'managed' or 'staged'
                _type: string, 'movie' or 'tvshow'
                showtitle: string, any show title
                order: string, any single column.
        """
        sql_comm = ('''SELECT
                            *
                        FROM
                            %s
                        WHERE
                            status="%s"''' % (_type, status)
                    )
        self.cur.execute(sql_comm)
        for content in self.cur.fetchall():
            json_item = build_json_item(content)
            yield build_contentmanager(self, build_contentitem(json_item))

    @logged_function
    def get_season_items(self, status, showtitle):
        """Get seasons of a show and return as ContentManager object."""
        self.cur.execute('''
                            SELECT
                                *
                            FROM
                                tvshow
                            WHERE
                                status = '%s'
                            AND
                                showtitle = '%s'
                            ORDER BY
                            CAST(season AS INTEGER)''' % (status, showtitle)
                         )
        for content in self.cur.fetchall():
            json_item = build_json_item(content)
            yield build_contentmanager(self, build_contentitem(json_item))

    @logged_function
    def get_episode_items(self, status, showtitle, season):
        """Get episodes of a show and return as a ContentManager object."""
        # TODO: Revise this function
        sql_comm = '''
                    SELECT
                        *
                    FROM
                        tvshow
                    WHERE
                        status='%s'
                    AND
                        showtitle='%s'
                    AND
                        season=%s
                    ORDER BY CAST
                        (season AS INTEGER),
                    CAST
                        (episode AS INTEGER)'''
        self.cur.execute(
            sql_comm % (status, showtitle, season)
        )
        for content in self.cur.fetchall():
            json_item = build_json_item(content)
            yield build_contentmanager(self, build_contentitem(json_item))

    @logged_function
    def get_synced_dirs(self, synced_type=None):
        """Get all items in synced cast as a list of dicts."""
        sql_templ = '''SELECT
                            *
                        FROM
                            synced'''
        params = ()
        if synced_type:
            sql_templ += ' WHERE type=?'
            params = (synced_type, )
        sql_templ += ''' ORDER BY
                            (
                                CASE WHEN
                                    label
                                LIKE
                                    'the %'
                                THEN
                                    substr(label,5)
                                ELSE
                                    label
                                END
                            ) COLLATE NOCASE'''
        self.cur.execute(sql_templ, params)
        return [SyncedItem(*x) for x in self.cur.fetchall()]

    @logged_function
    def delete_item_from_table(self, _type, file):
        """Delete an entry in the table using the 'file' key, regardless of status."""
        self.cur.execute(
            ' '.join(
                [
                    self.DELETE_DICT_QUERY[_type],
                    "WHERE file=:file"
                ]
            ),
            {'file': file}
        )
        self.conn.commit()

    @logged_function
    def delete_item_from_table_with_status_or_showtitle(self, _type, status, showtitle=None):
        """
        Delete an entry in the table using the 'status' and 'showtitle', key.

        Without showtitle, all entries will be deleted.

        Keys:
            - status = ['staged', 'managed']
        """
        self.cur.execute(
            ' '.join(
                [
                    self.DELETE_DICT_QUERY[_type],
                    "WHERE status=:status",
                    "AND showtitle=:showtitle" if showtitle else '',
                ]
            ),
            {
                'status': status,
                'showtitle': showtitle
            }
        )
        self.conn.commit()

    @logged_function
    def delete_item_from_table_with_season(self, _type, showtitle, season):
        """Delete an entry in the table using the 'showtitle' and 'season' key."""
        self.cur.execute(
            ' '.join(
                [
                    self.DELETE_DICT_QUERY[_type],
                    "WHERE showtitle=:showtitle AND season=:season"
                ]
            ),
            {
                'season': season,
                'showtitle': showtitle
            }
        )
        self.conn.commit()

    @logged_function
    def delete_entrie_from_blocked(self, value, _type):
        """Delete one entrie from blocked."""
        self.cur.execute(
            '''DELETE FROM
                    blocked
                WHERE
                            showtitle="%s"
                        AND
                    type=:type''',
            {'value': value, 'type': _type}
        )
        self.conn.commit()

    @logged_function
    def delete_all_from_synced(self):
        """Remove all dirs from synced."""
        self.cur.execute('DELETE FROM synced')
        self.conn.commit()

    @logged_function
    def delete_dir_from_synced(self, file):
        """Remove one dir from synced."""
        self.cur.execute(
            "DELETE FROM synced WHERE file=?",
            {'file': file}
        )
        self.conn.commit()

        self.conn.commit()

    @logged_function
    def remove_synced_dir(self, path):
        """Remove the entry in synced with the specified file."""
        # remove entry
        self.cur.execute(
            "DELETE FROM synced WHERE file=?",
            (path, )
        )
        self.conn.commit()

    @logged_function
    def update_content(self, file, _type, status=None, title=None):
        """Update a single field for item in Content with specified path."""
        # TODO: Verify there's only one entry in kwargs
        sql_comm = (
            '''UPDATE %s SET {0}=(?) WHERE file=?''' % _type
        )
        params = (file, )
        if status:
            sql_comm = sql_comm.format('status')
            params = (status, ) + params
        elif title:
            sql_comm = sql_comm.format('title')
            params = (title, ) + params
        # update item
        self.cur.execute(sql_comm, params)
        self.conn.commit()
