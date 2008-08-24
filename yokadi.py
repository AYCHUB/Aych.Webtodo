#!/usr/bin/env python
# -*- coding: UTF-8 -*-
""" Command line oriented, sqlite powered, todo list
@author: Aurélien Gâteau <aurelien.gateau@free.fr>
@license: undefined
"""

import os
import sys
import readline
from cmd import Cmd
from optparse import OptionParser

from sqlobject import *

import db
from taskcmd import TaskCmd
from projectcmd import ProjectCmd
from keywordcmd import KeywordCmd
from bugcmd import BugCmd
from utils import YokadiException

class YokadiCmd(Cmd, TaskCmd, ProjectCmd, KeywordCmd, BugCmd):
    def __init__(self):
        Cmd.__init__(self)
        TaskCmd.__init__(self)
        ProjectCmd.__init__(self)
        KeywordCmd.__init__(self)
        BugCmd.__init__(self)
        self.prompt = "yokadi> "
        self.historyPath=os.path.expandvars("$HOME/.yokadi_history")
        self.loadHistory()

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

    def onecmd(self, line):
        """This method is subclassed just to be
        able to encapsulate it with a try/except bloc"""
        try:
            return Cmd.onecmd(self, line)
        except YokadiException, e:
            print "*** Yokadi error ***\n\t%s" % e
        except Exception, e:
             print "*** Unhandled error (oups)***\n\t%s" % e
             print "This is a bug of Yokadi, sorry"

    def loadHistory(self):
        """Tries to load previous history list from disk"""
        try:
            readline.read_history_file(self.historyPath)
        except Exception, e:
            # Cannot load any previous history. Start from a clear one
            pass

    def writeHistory(self):
        """Writes shell history to disk"""
        try:
            # Open r/w and close file to create one if needed
            historyFile=file(self.historyPath, "w")
            historyFile.close()
            readline.set_history_length(1000)
            readline.write_history_file(self.historyPath)
        except Exception, e:
            raise YokadiException("Fail to save history to %s. Error was:\n\t%s"
                        % (self.historyPath, e))

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
    # Save history
    cmd.writeHistory()

if __name__=="__main__":
    main()
# vi: ts=4 sw=4 et
