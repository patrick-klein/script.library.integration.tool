#!/usr/bin/python
# -*- coding: utf-8 -*-

'''Defines the DatabaseHandler class'''

import sqlite3

from os.path import join

from resources import NEVER
from resources import ALWAYS
from resources import WITH_EPID
from resources import WITH_METADATA

from resources import AUTO_ADD_MOVIES
from resources import AUTO_ADD_TVSHOWS

from resources.lib import build_json_item
from resources.lib import build_contentitem
from resources.lib import build_contentmanager

from resources.lib.log import logged_function

from resources.lib.utils import utf8_args
from resources.lib.utils import MANAGED_FOLDER

from resources.lib.items.blocked import BlockedItem
from resources.lib.items.synced import SyncedItem


class Database(object):
    '''Database class with all database methods.'''

    #TODO: Reimplement blocked keywords
    #TODO: Combine remove_content_item functions using **kwargs
    #TODO: use movie, tvshow as a table_name,
    #the __init__ method to create tables need be updated,
    #the objective is reduce the if's in all plaves
    def __init__(self):
        # Connect to database
        self.conn = sqlite3.connect(join(MANAGED_FOLDER, 'managed.db'))
        self.conn.text_factory = str
        self.cur = self.conn.cursor()
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
        # Close connection when deleted
        self.conn.close()


    @utf8_args
    @logged_function
    def add_blocked_item(self, value, _type):
        '''Add an item to blocked with the specified values'''
        # Ignore if already in table
        if not self.check_blocked(value, _type):
            self.cur.execute("INSERT INTO blocked (value, type) VALUES (?, ?)", (value, _type))
            self.conn.commit()


    @utf8_args
    @logged_function
    def add_content_item(self, jsondata):
        '''Add content to library'''
        query_defs = tuple()
        sql_comm ='''
            INSERT OR IGNORE INTO
                {table}
                %s
            VALUES
                %s'''.format(table=jsondata['type'])
        contentmanager = build_contentmanager(
            self,
            jsondata
        )
        # sqlite named style:
        if jsondata['type'] == 'tvshow':
            query_defs = (
                '''(
                    file,
                    title,
                    type,
                    status,
                    year,
                    showtitle,
                    season,
                    episode
                    )''',
                '''(
                    :file,
                    :title,
                    :type,
                    'staged',
                    :year,
                    :showtitle,
                    :season,
                    :episode
                    )'''
            )
            self.cur.execute(sql_comm % query_defs, jsondata)
            self.conn.commit()
            if AUTO_ADD_TVSHOWS != NEVER:
                if AUTO_ADD_TVSHOWS == WITH_EPID:
                    contentmanager.add_to_library()
                elif AUTO_ADD_TVSHOWS == WITH_METADATA:
                    contentmanager.add_to_library_if_metadata()
        elif jsondata['type'] == 'movie':
            query_defs = (
                '''(
                    file,
                    title,
                    type,
                    status,
                    year
                    )''',
                '''(
                    :file,
                    :title,
                    :type,
                    'staged',
                    :year
                    )'''
            )
            self.cur.execute(sql_comm % query_defs, jsondata)
            self.conn.commit()
            if AUTO_ADD_MOVIES != NEVER:
                if AUTO_ADD_MOVIES == ALWAYS:
                    contentmanager.add_to_library()
                elif AUTO_ADD_MOVIES == WITH_METADATA:
                    contentmanager.add_to_library_if_metadata()
        elif jsondata['type'] == 'music':
            # TODO: Music params
            raise NotImplementedError(
                'Not implemented yet'
            )


    @utf8_args
    @logged_function
    def add_synced_dir(self, label, path, _type):
        '''Create an entry in synced with specified values'''
        self.cur.execute(
            '''INSERT OR REPLACE INTO
                    synced(file, label, type)
                VALUES
                    (?, ?, ?)''', (path, label, _type)
        )
        self.conn.commit()


    @utf8_args
    @logged_function
    def check_blocked(self, value, _type):
        '''Return True if the given entry is in blocked'''
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
        '''Query Content table for all (not null) distinct showtitles
        and cast results as list of strings'''
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
        '''Return all items in blocked as a list of BlockedItem objects'''
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
        '''Query Content table for sorted items with given constaints
        and casts results as contentitem subclasses
        keyword arguments:
            status: string, 'managed' or 'staged'
            _type: string, 'movie' or 'tvshow'
            showtitle: string, any show title
            order: string, any single column'''
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
        self.cur.execute(
            '''
                SELECT DISTINCT CAST
                    (season AS INTEGER)
                FROM
                    tvshow
                WHERE
                    status='%s'
                AND
                    showtitle='%s'
                ORDER BY
                    CAST(season AS INTEGER)''' % (status, showtitle)
        )
        for content in self.cur.fetchall():
            yield int(*content)


    @logged_function
    def get_episode_items(self, status, showtitle, season):
        sql_comm ='''
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


    @utf8_args
    @logged_function
    def get_synced_dirs(self, synced_type=None):
        '''Get all items in synced cast as a list of dicts'''
        sql_templ = '''SELECT
                            *
                        FROM
                            synced'''
        params = ()
        if synced_type:
            sql_templ += ' WHERE type=?'
            params = (synced_type, )
        sql_templ += '''ORDER BY
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


    @utf8_args
    @logged_function
    def load_item(self, path):
        '''Query a single item and return as a json'''
        self.cur.execute('''SELECT
                                *
                            FROM
                                Content
                            WHERE
                                file="%s"''', path)
        return build_json_item(self.cur.fetchone())


    @utf8_args
    @logged_function
    def path_exists(self, file):
        '''Return True if path is already in database (with given status)
            This function can return a list with multple values
            with name of the tables where item exist'''
        tables = list()
        for table in ['movie', 'tvshow']:
            sql_comm = (
               '''
                    SELECT
                        status
                    FROM
                        '%s'
                    WHERE
                        file="%s"''' % (table, file)
                )
            result = self.cur.execute(sql_comm).fetchone()
            if result:
                tables.append(*list(result))
        return tables


    @utf8_args
    @logged_function
    def remove_from(self,
                    status=None,
                    _type=None,
                    showtitle=None,
                    file=None,
                    season=None):
        '''Remove all items colected with sqlquerys'''
        STR_CMD_QUERY = "DELETE FROM %s" % _type
        if showtitle:
            STR_CMD_QUERY += '''
                        WHERE
                            status="%s"
                        AND
                            showtitle="%s"
                        ''' % (status, showtitle)
        elif showtitle and file:
            STR_CMD_QUERY += '''
                        WHERE
                            status="%s"
                        AND
                            type="%s"
                        ''' % (status, _type)
        elif file:
            STR_CMD_QUERY += '''
                        WHERE
                            file="%s"
                        ''' % (file)
        elif season:
            STR_CMD_QUERY += '''
                        WHERE
                            showtitle="%s"
                        AND
                            season="%s"
                        ''' % (showtitle, season)

        self.cur.execute(STR_CMD_QUERY)
        self.conn.commit()


    @logged_function
    def remove_all_synced_dirs(self):
        '''Delete all entries in synced'''
        # remove all rows
        self.cur.execute('DELETE FROM synced')
        self.conn.commit()


    @utf8_args
    @logged_function
    def remove_blocked(self, value, _type):
        '''Remove the item in blocked with the specified parameters'''
        self.cur.execute('''DELETE FROM
                                blocked
                            WHERE
                                value=?
                            AND
                                type=?''', (value, _type)
        )
        self.conn.commit()


    @utf8_args
    @logged_function
    def remove_synced_dir(self, path):
        '''Remove the entry in synced with the specified file'''
        # remove entry
        self.cur.execute(
            "DELETE FROM synced WHERE file=?",
            (path, )
        )
        self.conn.commit()


    @utf8_args
    @logged_function
    def update_content(self, file, _type, status=None, title=None):
        '''Update a single field for item in Content with specified path'''
        #TODO: Verify there's only one entry in kwargs
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
