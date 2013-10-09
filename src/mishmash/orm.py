# -*- coding: utf-8 -*-
################################################################################
#  Copyright (C) 2012  Travis Shirk <travis@pobox.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
################################################################################
import os
import datetime
import sqlalchemy as sql
from sqlalchemy import orm, event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from .info import VERSION


VARIOUS_ARTISTS_NAME = u"Various Artists"


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    '''Allows foreign keeys to work in sqlite.'''
    import sqlite3
    if dbapi_connection.__class__ is sqlite3.Connection:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


Base = declarative_base()

artist_labels = sql.Table("artist_labels", Base.metadata,
                          sql.Column("artist_id", sql.Integer,
                                     sql.ForeignKey("artists.id")),
                          sql.Column("label_id", sql.Integer,
                                     sql.ForeignKey("labels.id")),
                         )

album_labels = sql.Table("album_labels", Base.metadata,
                         sql.Column("album_id", sql.Integer,
                                    sql.ForeignKey("albums.id")),
                         sql.Column("label_id", sql.Integer,
                                    sql.ForeignKey("labels.id")),
                        )

track_labels = sql.Table("track_labels", Base.metadata,
                         sql.Column("track_id", sql.Integer,
                                    sql.ForeignKey("tracks.id")),
                         sql.Column("label_id", sql.Integer,
                                    sql.ForeignKey("labels.id")),
                        )

artist_images = sql.Table("artist_images", Base.metadata,
                          sql.Column("artist_id", sql.Integer,
                                     sql.ForeignKey("artists.id")),
                          sql.Column("img_id", sql.Integer,
                                     sql.ForeignKey("images.id")),
                         )

album_images = sql.Table("album_images", Base.metadata,
                         sql.Column("album_id", sql.Integer,
                                    sql.ForeignKey("albums.id")),
                         sql.Column("img_id", sql.Integer,
                                    sql.ForeignKey("images.id")),
                        )


class OrmObject(object):
    @staticmethod
    def initTable(session):
        pass

    def __repr__(self):
        attrs = []
        for key in self.__dict__:
            if not key.startswith('_'):
                attrs.append((key, getattr(self, key)))
        return self.__class__.__name__ + '(' + ', '.join(x[0] + '=' +
                                            repr(x[1]) for x in attrs) + ')'


class Meta(Base, OrmObject):
    __tablename__ = "meta"

    # Columns
    version = sql.Column(sql.String(32), nullable=False, primary_key=True)
    last_sync = sql.Column(sql.DateTime)

    @staticmethod
    def initTable(session):
        session.add(Meta(version=VERSION))


def _getSortName(context):
    from . import util
    name, prefix = util.splitNameByPrefix(context.current_parameters["name"])
    return u"%s, %s" % (name, prefix) if prefix else name

class Artist(Base, OrmObject):
    __tablename__ = "artists"

    # Columns
    id = sql.Column(sql.Integer, primary_key=True)
    name = sql.Column(sql.Unicode(128), nullable=False, index=True)
    sort_name = sql.Column(sql.Unicode(128), nullable=False,
                           default=_getSortName, onupdate=_getSortName)
    date_added = sql.Column(sql.DateTime(), nullable=False,
                            default=datetime.datetime.now)

    # Relations
    albums = orm.relation("Album", cascade="all")
    '''all albums by the artist'''
    tracks = orm.relation("Track", cascade="all")
    '''all tracks by the artist'''
    labels = orm.relation("Label", secondary=artist_labels)
    '''one-to-many (artist->label) and many-to-one (label->artist)'''
    images = orm.relation("Image", secondary=artist_images, cascade="all")
    '''one-to-many artist images.'''

    @staticmethod
    def initTable(session):
        session.add(Artist(name=VARIOUS_ARTISTS_NAME))


class Album(Base, OrmObject):
    __tablename__ = "albums"
    __table_args__ = (sql.UniqueConstraint("title",
                                           "artist_id"), {})

    # Columns
    id = sql.Column(sql.Integer, primary_key=True)
    title = sql.Column(sql.Unicode(128), nullable=False, index=True)
    date_added = sql.Column(sql.DateTime(), nullable=False,
                            default=datetime.datetime.now)
    release_date = sql.Column(sql.String(24))
    original_release_date = sql.Column(sql.String(24))
    recording_date = sql.Column(sql.String(24))
    compilation = sql.Column(sql.Boolean(), nullable=False, default=False)

    # Foreign keys
    artist_id = sql.Column(sql.Integer, sql.ForeignKey("artists.id"),
                           nullable=False, index=True)

    # Relations
    artist = orm.relation("Artist")
    tracks = orm.relation("Track", cascade="all")
    labels = orm.relation("Label", secondary=album_labels)
    images = orm.relation("Image", secondary=album_images, cascade="all")
    '''one-to-many album images.'''


class Track(Base, OrmObject):
    __tablename__ = "tracks"

    # Columns
    id = sql.Column(sql.Integer, primary_key=True)
    path = sql.Column(sql.String(512), nullable=False, unique=True, index=True)
    size_bytes = sql.Column(sql.Integer, nullable=False)
    ctime = sql.Column(sql.DateTime(), nullable=False)
    mtime = sql.Column(sql.DateTime(), nullable=False)
    date_added = sql.Column(sql.DateTime(), nullable=False,
                            default=datetime.datetime.now)
    time_secs = sql.Column(sql.Integer, nullable=False)
    title = sql.Column(sql.Unicode(128), nullable=False, index=True)
    track_num = sql.Column(sql.SmallInteger)
    track_total = sql.Column(sql.SmallInteger)
    media_num = sql.Column(sql.SmallInteger)
    media_total = sql.Column(sql.SmallInteger)
    bit_rate = sql.Column(sql.SmallInteger)
    variable_bit_rate = sql.Column(sql.Boolean)

    # Foreign keys
    artist_id = sql.Column(sql.Integer, sql.ForeignKey("artists.id"),
                           nullable=False, index=True)
    album_id = sql.Column(sql.Integer, sql.ForeignKey("albums.id"),
                          nullable=True, index=True)
    # Relations
    artist = orm.relation("Artist")
    album = orm.relation("Album")
    labels = orm.relation("Label", secondary=track_labels)

    def __init__(self, **kwargs):
        '''Along with the column args a ``audio_file`` keyword may be passed
        for this class to use for initialization.'''

        if "audio_file" in kwargs:
            self.update(kwargs["audio_file"])
            del kwargs["audio_file"]

        super(Track, self).__init__(**kwargs)

    def update(self, audio_file):
        path = audio_file.path
        tag = audio_file.tag
        info = audio_file.info

        self.path = path
        self.size_bytes = info.size_bytes
        self.ctime = datetime.datetime.fromtimestamp(os.path.getctime(path))
        self.mtime = datetime.datetime.fromtimestamp(os.path.getmtime(path))
        self.time_secs = info.time_secs
        self.title = tag.title
        self.track_num, self.track_total = tag.track_num
        self.variable_bit_rate, self.bit_rate = info.bit_rate
        self.media_num, self.media_total = tag.disc_num


class Label(Base, OrmObject):
    __tablename__ = "labels"

    # Columns
    id = sql.Column(sql.Integer, primary_key=True)
    name = sql.Column(sql.Unicode(64), nullable=False, unique=True)


class Image(Base, OrmObject):
    __tablename__ = "images"

    _types_enum = sql.Enum("ARTIST",
                           "FRONT_COVER", "GATEFOLD_COVER", "BACK_COVER",
                           name="image_types")

    id = sql.Column(sql.Integer, primary_key=True)
    type = sql.Column(_types_enum, nullable=False)
    mime_type = sql.Column(sql.String(32), nullable=False)
    md5 = sql.Column(sql.String(32), nullable=False)
    size = sql.Column(sql.Integer, nullable=False)
    data = sql.Column(sql.LargeBinary, nullable=False)


TYPES  = [Meta, Label, Artist, Album, Track, Image]
LABELS = [artist_labels, album_labels, track_labels,
          artist_images, album_images]
TABLES = [T.__table__ for T in TYPES] + LABELS
'''All the table instances.  Order matters (esp. for postgresql). The
tables are created in normal order, and dropped in reverse order.'''
ENUMS = [Image._types_enum]
