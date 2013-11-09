# -*- coding: utf-8 -*-
################################################################################
#  Copyright (C) 2013  Travis Shirk <travis@pobox.com>
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
import sys
from pyramid.config import Configurator
from zope.sqlalchemy import ZopeTransactionExtension

from .. import database


def _configure(settings, DBSession):
    config = Configurator(settings=settings)

    config.include('pyramid_chameleon')
    config.include('pyramid_layout')

    def _DBSession(request):
        return DBSession
    config.add_request_method(_DBSession, name="DBSession", reify=True)

    config.add_static_view('static', 'static', cache_max_age=3600)

    config.add_route('pyramid', '/pyramid')
    config.add_route('home', '/')
    config.add_route('search', '/search')

    config.add_route('all_artists', '/artists')
    config.add_route('artist', '/artist/{id:\d+}')
    config.add_route('images.covers', '/images/covers/{id:\d+|default}')

    config.scan(".panels")
    config.scan(".layouts")
    config.scan(".views")
    config.scan(".events")

    return config


def main(global_config, **settings):

    engine_args = dict(database.DEFAULT_ENGINE_ARGS)
    pfix, plen = "sqlalchemy.", len("sqlalchemy.")
    # Strip prefix and remove url value
    sql_ini_args = {
            name[plen:]: settings[name]
                for name in settings if name.startswith(pfix) and
                                        not name.endswith(".url")
            }
    engine_args.update(sql_ini_args)

    session_args = {"extension": ZopeTransactionExtension()}

    (engine,
     DBSession) = database.init(settings["%surl" % pfix],
                                engine_args=engine_args,
                                session_args=session_args)

    try:
        database.check(engine)
    except database.MissingSchemaException as ex:
        print("Missing tables: %s" % str(ex.tables))
        print("\nRun `mishmash init`")
        sys.exit(1)


    config = _configure(settings, DBSession)

    return config.make_wsgi_app()
