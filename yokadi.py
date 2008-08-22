#!/usr/bin/env python
import os
import sys
from cmd import Cmd
from optparse import OptionParser

from sqlobject import *

import db
from taskcmd import TaskCmd
from projectcmd import ProjectCmd
from keywordcmd import KeywordCmd
from bugcmd import BugCmd

class YokadiCmd(Cmd, TaskCmd, ProjectCmd, KeywordCmd, BugCmd):
    def __init__(self):
        Cmd.__init__(self)
        TaskCmd.__init__(self)
        ProjectCmd.__init__(self)
        KeywordCmd.__init__(self)
        BugCmd.__init__(self)
        self.prompt = "yokadi> "

    def emptyline(self):
        """Executed when input is empty. Reimplemented to do nothing."""
        return

    def default(self, line):
        if line.isdigit():
            self.do_t_show(line)
        else:
            Cmd.default(self, line)

    def do_EOF(self, line):
        """Quit."""
        print
        return True


def main():
    parser = OptionParser()

    parser.add_option("--db", dest="filename",
                      help="TODO database", metavar="FILE")

    parser.add_option("--create-only",
                      dest="createOnly", default=False, action="store_true",
                      help="Just create an empty database")

    (options, args) = parser.parse_args()

    dbFileName = os.path.abspath(options.filename)
    connectionString = 'sqlite:' + dbFileName
    connection = connectionForURI(connectionString)
    sqlhub.processConnection = connection
    if not os.path.exists(dbFileName):
        print "Creating database"
        db.createTables()

    if options.createOnly:
        return

    cmd = YokadiCmd()
    try:
        if len(args) > 0:
            cmd.onecmd(" ".join(args))
        else:
            cmd.cmdloop()
    except KeyboardInterrupt:
        print "\n\tBreak !"
        sys.exit(1)

if __name__=="__main__":
    main()
# vi: ts=4 sw=4 et
