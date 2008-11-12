#!/usr/bin/env python
"""
This script updates a Yokadi database to the latest version

How the update process works (assuming current version is x and target version
is x+n, database version x is old.db and database version x+n is new.db):

- Create a copy of old.db
- for v in range(x, x + n):
-   run update<v>to<v+1>.updateDb()
- Create a data-only SQL dump of the database
- Create an empty database in new.db
- Restore the dump in new.db

The final dump/restore state ensures that:
- All fields are created in the same order (when adding a new column, you can't
  specify its position)
- All constraints are in place (when adding a new column, you can't mark it
  'non null')
- The update process really creates the same structure as db.createDatabase()

Restoring the dump is done in a separate script because we use Yokadi table
definitions, but the update scripts might have defined them differently.
"""
import os
import subprocess
import sys
import shutil
from optparse import OptionParser

from sqlobject import connectionForURI

import dump
import update1to2

CURRENT_DB_VERSION = 2

def getVersion(fileName):
    cx = connectionForURI('sqlite:' + fileName)
    if not cx.tableExists("config"):
        return 1
    row = cx.queryOne("select value from config where name='DB_VERSION'")
    return int(row[0])


def createWorkDb(fileName):
    name = os.path.join(os.path.dirname(fileName), "work.db")
    shutil.copy(fileName, name)
    return name


def createFinalDb(workFileName, finalFileName):
    dumpFileName = "dump.sql"
    print "Dumping into %s" % dumpFileName
    dumpFile = file(dumpFileName, "w")
    dump.dumpDatabase(workFileName, dumpFile)
    dumpFile.close()

    print "Restoring dump from %s into %s" % (dumpFileName, finalFileName)
    err = subprocess.call(["/usr/bin/python", "restore.py", finalFileName,
    dumpFileName])
    if err != 0:
        raise Exception("restore.py failed")


def main():
    # Parse args
    parser = OptionParser()

    parser.usage = "%prog <path/to/old.db> <path/to/updated.db>"
    (options, args) = parser.parse_args()
    if len(args) != 2:
        parser.error("Wrong argument count")

    dbFileName = args[0]
    newDbFileName = args[1]
    if not os.path.exists(dbFileName):
        parser.error("'%s' does not exist" % dbFileName)

    if os.path.exists(newDbFileName):
        parser.error("'%s' already exists" % newDbFileName)

    dbFileName = os.path.abspath(dbFileName)

    # Check version
    version = getVersion(dbFileName)
    print "Found version %d" % version
    if version == CURRENT_DB_VERSION:
        print "Nothing to do"
        return 0

    # Start import
    workDbFileName = createWorkDb(dbFileName)

    while True:
        version = getVersion(workDbFileName)
        if version == CURRENT_DB_VERSION:
            break
        scriptFileName = os.path.abspath("update%dto%d" % (version, version + 1))
        print "Running %s" % scriptFileName
        err = subprocess.call([scriptFileName, workDbFileName])
        if err != 0:
            print "Update failed."
            return 2

    createFinalDb(workDbFileName, newDbFileName)

    return 0


if __name__ == "__main__":
    sys.exit(main())
# vi: ts=4 sw=4 et
