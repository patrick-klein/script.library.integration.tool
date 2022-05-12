# -*- coding: utf-8 -*-

"""Defines the DatabaseHandler class."""

import xbmc
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


class Database():
    """Database class with all database methods."""

    # TODO: Reimplement blocked keywords
    # TODO: Combine remove_content_item functions using **kwargs
    def __init__(self):
        """__init__ database."""

        # Connect to database
        self.conn = sqlite3.connect(join(MANAGED_FOLDER, 'managed.db'))
        self.conn.text_factory = str
        self.cur = self.conn.cursor()
        self.UPDATE_DICT_QUERY = {
            "movie": "UPDATE movie",
            "tvshow": "UPDATE tvshow",
            "music": "UPDATE music",
        }
        self.DELETE_DICT_QUERY = {
            "movie": "DELETE FROM movie",
            "tvshow": "DELETE FROM tvshow",
            "music": "DELETE FROM music",
        }
        self.INSERT_DICT_QUERY = {
            "movie": "INSERT OR IGNORE INTO movie",
            "tvshow": "INSERT OR IGNORE INTO tvshow",
            "music": "INSERT OR IGNORE INTO music",
        }
        self.SELECT_DICT_QUERY = {
            'movie': 'SELECT * FROM movie',
            'tvshow': 'SELECT * FROM tvshow',
            'music': 'SELECT * FROM music',
            'blocked': 'SELECT * FROM blocked',
            'synced': 'SELECT * FROM synced',
            'content': 'SELECT * FROM content',
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
    def check_if_is_blocked(self, value, _type=None):
        """Check if value exist in blocked and return True else None """
        self.cur.execute(
            ' '.join(
                [
                    self.SELECT_DICT_QUERY['blocked'],
                    "WHERE value=:value",
                    "AND type=:type" if _type else '',
                ]
            ), {'value': value, 'type': _type}
        )
        return True if self.cur.fetchone() else None

    @logged_function
    def load_item(self, file):
        """Query a single item and return as a json."""
        self.cur.execute(
            ' '.join(
                [
                    self.SELECT_DICT_QUERY['content'],
                    "WHERE file=:file"
                ]
            ), {'file': file}
        )
        return build_json_item(self.cur.fetchone())

    @logged_function
    def path_exists(self, file):
        """
        Check if item exist in all tables.

        If exist return a list with table and type else None.
        """
        table = None
        status = None
        for table_type in ['movie', 'tvshow']:
            LOCAL_SELECT_DICT_QUERY = {
                "movie": "SELECT status FROM movie",
                "tvshow": "SELECT status FROM tvshow"
            }
            sql_comm = (
                ' '.join(
                    [
                        LOCAL_SELECT_DICT_QUERY[table_type],
                        "WHERE file=:file",
                    ]
                )
            )
            result = self.cur.execute(
                sql_comm,
                {'file': file}
            ).fetchone()
            if result:
                table = table_type
                status = result[0]
        if table and status:
            return [table, status]
        else:
            return None

    @logged_function
    def add_blocked_item(self, value, _type):
        """Add an item to blocked with the specified values."""
        # Ignore if already in table
        if not self.check_if_is_blocked(value, _type):
            self.cur.execute(
                "INSERT INTO blocked (value, type) VALUES (?, ?)", (value, _type))
            self.conn.commit()

    @logged_function
    def add_content_item(self, jsondata):
        """Add content to library."""
        _type = jsondata['type']
        query_defs = {
            'tvshow': (
                "(file,title,type,status,year,showtitle,season,episode)",
                "(:file,:title,:type,'staged',:year,:showtitle,:season,:episode)"
            ),
            'movie': (
                "(file,title,type,status,year)",
                "(:file,:title,:type,'staged',:year)"
            ),
            'music': ValueError("Not implemented yet, music")
        }
        # sqlite named style:
        self.cur.execute(
            ' '.join(
                [
                    self.INSERT_DICT_QUERY[_type],
                    '%s VALUES %s' % query_defs[_type],
                ]
            ), jsondata
        )
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
    def add_item_to_synced(self, label, path, _type):
        """Create an entry in synced with specified values."""
        self.cur.execute(
            '''INSERT OR REPLACE INTO
                    synced
                    (file, label, type)
                VALUES
                    (:file, :label, :type)
            ''',
            {
                'file': path,
                'label': label,
                'type': _type
            }
        )
        self.conn.commit()

    @logged_function
    def get_all_blocked_itens(self):
        """Return all items in blocked as a list of BlockedItem objects."""
        self.cur.execute(
            ' '.join(
                [
                    self.SELECT_DICT_QUERY['blocked'],
                    "ORDER BY type, value"
                ]
            )
        )
        return [BlockedItem(*x) for x in self.cur.fetchall()]

    @logged_function
    def get_all_shows(self, status):
        """
            Query Content table for all (not null) distinct showtitles.
                Cast results as list of strings.
        """
        # Query database
        self.cur.execute(
            '''
            SELECT DISTINCT
                showtitle
            FROM
                tvshow
            WHERE
                status=:status
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
                ) COLLATE NOCASE''',
            {'status': status}
        )
        for item in self.cur.fetchall():
            yield item[0]

    @logged_function
    def get_content_items(self, status, _type):
        """
        Query Content table for sorted items with given constaints.

            Casts results as contentitem subclasses.

            keyword arguments:
                status: string, 'managed' or 'staged'
                _type: string, 'movie' or 'tvshow'
                showtitle: string, any show title
                order: string, any single column.
        """
        self.cur.execute(
            ' '.join(
                [
                    self.SELECT_DICT_QUERY[_type],
                    "WHERE status=:status"
                ]
            ),
            {'status': status}
        )
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
                            status=:status
                        AND
                            showtitle=:showtitle
                        ORDER BY
                        CAST(season AS INTEGER)''',
                         {
                             'status': status,
                             'showtitle': showtitle,
                         }
                         )
        for content in self.cur.fetchall():
            json_item = build_json_item(content)
            yield build_contentmanager(self, build_contentitem(json_item))

    @logged_function
    def get_episode_items(self, status, showtitle, season):
        """Get episodes of a show and return as a ContentManager object."""
        sql_comm = '''
                    SELECT
                        *
                    FROM
                        tvshow
                    WHERE
                        status=:status
                    AND
                        showtitle=:showtitle
                    AND
                        season=:season
                    ORDER BY CAST
                        (season AS INTEGER),
                    CAST
                        (episode AS INTEGER)'''
        self.cur.execute(
            sql_comm,
            {
                'status': status,
                'showtitle': showtitle,
                'season': season
            }
        )
        for content in self.cur.fetchall():
            json_item = build_json_item(content)
            yield build_contentmanager(self, build_contentitem(json_item))

    @logged_function
    def get_synced_dirs(self, synced_type=None):
        """Get all itens in synced or itens by type."""
        orderby_str = '''ORDER BY
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
        self.cur.execute(
            ' '.join(
                [
                    self.SELECT_DICT_QUERY['select'],
                    "WHERE type=:type" if synced_type else '',
                    orderby_str
                ]
            ), {'type': synced_type}
        )
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
                    value="%s"
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

    @logged_function
    def update_title_in_database(self, file, _type, title):
        """Update a title for a single entrie in database."""
        self.cur.execute(
            ' '.join(
                [
                    self.UPDATE_DICT_QUERY[_type],
                    'SET title=:title WHERE file=:file',
                ]
            ), {'file': file, 'type': _type, 'title': title}
        )
        self.conn.commit()

    @logged_function
    def update_showtitle_in_database(self, file, _type, showtitle):
        """Update a showtitle for a single entrie in database."""
        self.cur.execute(
            ' '.join(
                [
                    self.UPDATE_DICT_QUERY[_type],
                    'SET showtitle=:showtitle WHERE file=:file'
                ]
            ), {'file': file, 'type': _type, 'showtitle': showtitle}
        )
        self.conn.commit()

    @logged_function
    def update_status_in_database(self, file, _type, status):
        """Update a status for a single entrie in database."""
        self.cur.execute(
            ' '.join(
                [
                    self.UPDATE_DICT_QUERY[_type],
                    'SET status=:status WHERE file=:file',
                ]
            ), {'file': file, 'type': _type, 'status': status}
        )
        self.conn.commit()
