import datetime
import pytest
from sqlalchemy.exc import IntegrityError, DataError
import mishmash
from mishmash.orm import (Meta, Library, Artist, ARTIST_NAME_LIMIT,
                          NULL_LIB_ID, NULL_LIB_NAME,
                          MAIN_LIB_ID, MAIN_LIB_NAME)


def test_meta_table(session):
    metadata = session.query(Meta).one()
    assert metadata.version == mishmash.version
    assert metadata.last_sync is None


def test_meta_table_write(session):
    metadata = session.query(Meta).one()
    metadata.version = "1.2.3"
    t = datetime.datetime.utcnow()
    metadata.last_sync = t
    session.add(metadata)
    session.commit()

    metadata = session.query(Meta).one()
    assert metadata.version == "1.2.3"
    assert metadata.last_sync == t


def test_libraries_table(session):
    # Default rows, for __null__ and Music
    default_rows = session.query(Library).all()
    assert len(default_rows) == 2
    assert default_rows[0].id == NULL_LIB_ID
    assert default_rows[0].name == NULL_LIB_NAME
    assert default_rows[0].last_sync is None
    assert default_rows[1].id == MAIN_LIB_ID
    assert default_rows[1].name == MAIN_LIB_NAME
    assert default_rows[1].last_sync is None


def test_ArtistNoLib(session):
    session.add(Artist(name="Pantera"))
    with pytest.raises(IntegrityError):
        session.commit()

def test_Artist(session, db_library):
    lid = db_library.id
    session.add(Artist(name="The Roots", lib_id=lid))
    session.commit()
    assert session.query(Artist).filter_by(name="The Roots", lib_id=lid).one()

def test_ArtistBig(session, db_library):
    lid = db_library.id
    godflesh = "!" * ARTIST_NAME_LIMIT
    session.add(Artist(name=godflesh, lib_id=lid))
    session.commit()
    assert session.query(Artist).filter_by(name=godflesh, lib_id=lid).one()

def test_ArtistTooBig(session, db_library, request):
    lid = db_library.id
    godflesh = "!" * (ARTIST_NAME_LIMIT + 1)
    session.add(Artist(name=godflesh, lib_id=lid))
    if "sqlite" in request.keywords:
        session.commit()
        assert session.query(Artist).filter_by(name=godflesh, lib_id=lid).one()
    else:
        with pytest.raises(DataError):
            session.commit()

