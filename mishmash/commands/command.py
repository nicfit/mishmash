# -*- coding: utf-8 -*-
################################################################################
#  Copyright (C) 2014  Travis Shirk <travis@pobox.com>
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
from .. import database


class Command(object):
    _all_commands = {}

    def __init__(self, help, subparsers=None):
        self.subparsers = subparsers
        self.parser = self.subparsers.add_parser(self.NAME, help=help)
        self.parser.set_defaults(func=self.run)

    def run(self, args, config):
        self.args = args
        self.config = config
        self.db_engine, self.db_session = database.init(self.config.db_url)
        return self._run()

    def _run(self):
        raise NotImplementedError("Must implement the run() function")

    @staticmethod
    def initAll(subparsers):
        for cmd in Command._all_commands.values():
            cmd(subparsers)


def register(CommandSubClass):
    # Gotta mae the command name a class var
    Command._all_commands[CommandSubClass.NAME] = CommandSubClass
    return CommandSubClass
