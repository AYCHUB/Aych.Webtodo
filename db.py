# -*- coding: UTF-8 -*-
"""
Database access layer using sqlobject

@author: Aurélien Gâteau <aurelien@.gateau@free.fr>
@license: GPLv3
"""

import os
import sys
try:
    from sqlobject import BoolCol, connectionForURI, DatabaseIndex, DateTimeCol, EnumCol, ForeignKey, IntCol, \
         RelatedJoin, sqlhub, SQLObject, SQLObjectNotFound, UnicodeCol
except ImportError:
    print "You must install SQLObject to use Yokadi"
    print "Get it on http://www.sqlobject.org/"
    print "Or use 'easy_install sqlobject'"
    sys.exit(1)

from yokadiexception import YokadiException
import tui

# Yokadi database version needed for this code
# If database config key DB_VERSION differs from this one a database migration
# is required
DB_VERSION = 2
DB_VERSION_KEY = "DB_VERSION"


class Project(SQLObject):
    class sqlmeta:
        defaultOrder = "name"
    name = UnicodeCol(alternateID=True, notNone=True)
    active = BoolCol(default=True)

    def __unicode__(self):
        return self.name


class Keyword(SQLObject):
    class sqlmeta:
        defaultOrder = "name"
    name = UnicodeCol(alternateID=True, notNone=True)
    tasks = RelatedJoin("Task",
        createRelatedTable=False,
        intermediateTable="task_keyword",
        joinColumn="keyword_id",
        otherColumn="task_id")


class TaskKeyword(SQLObject):
    task = ForeignKey("Task")
    keyword = ForeignKey("Keyword")
    value = IntCol(default=None)


class Task(SQLObject):
    title = UnicodeCol()
    creationDate = DateTimeCol(notNone=True)
    dueDate = DateTimeCol(default=None)
    doneDate = DateTimeCol(default=None)
    description = UnicodeCol(default="", notNone=True)
    urgency = IntCol(default=0, notNone=True)
    status = EnumCol(enumValues=['new', 'started', 'done'])
    project = ForeignKey("Project")
    keywords = RelatedJoin("Keyword",
        createRelatedTable=False,
        intermediateTable="task_keyword",
        joinColumn="task_id",
        otherColumn="keyword_id")
    uniqTaskTitlePerProject=DatabaseIndex(title, project, unique=True)

    def setKeywordDict(self, dct):
        """
        Defines keywords of a task.
        Dict is of the form: keywordName => value
        """
        for taskKeyword in TaskKeyword.selectBy(task=self):
            taskKeyword.destroySelf()

        for name, value in dct.items():
            keyword = Keyword.selectBy(name=name)[0]
            TaskKeyword(task=self, keyword=keyword, value=value)

    def getKeywordDict(self):
        """
        Returns all keywords of a task as a dict of the form:
        keywordName => value
        """
        dct = {}
        for keyword in TaskKeyword.selectBy(task=self):
            dct[keyword.keyword.name] = keyword.value
        return dct

    def getKeywordsAsString(self):
        """
        Returns all keywords as a string like "key1=value1, key2=value2..."
        """
        return ", ".join(list(("%s=%s" % k for k in self.getKeywordDict().items())))

class Config(SQLObject):
    """yokadi config"""
    class sqlmeta:
        defaultOrder = "name"
    name  = UnicodeCol(alternateID=True, notNone=True)
    value = UnicodeCol(default="", notNone=True)
    system = BoolCol(default=False, notNone=True)
    desc = UnicodeCol(default="", notNone=True)


TABLE_LIST = [Project, Keyword, Task, TaskKeyword, Config]

def createTables():
    for table in TABLE_LIST:
        table.createTable()


def getVersion():
    if not Config.tableExists():
        # There was no Config table in v1
        return 1

    try:
        return int(Config.byName(DB_VERSION_KEY).value)
    except SQLObjectNotFound:
        raise YokadiException("Configuration key '%s' does not exist. This should not happen!" % DB_VERSION_KEY)


def connectDatabase(dbFileName, createIfNeeded=True):
    """Connect to database and create it if needed
    @param dbFileName: path to database file
    @type dbFileName: str
    @param createIfNeeded: Indicate if database must be created if it does not exists (default True)
    @type createIfNeeded: bool"""

    dbFileName=os.path.abspath(dbFileName)

    if sys.platform == 'win32':
        connectionString = 'sqlite:/'+ dbFileName[0] +'|' + dbFileName[2:]
    else:
        connectionString = 'sqlite:' + dbFileName
        
    connection = connectionForURI(connectionString)
    sqlhub.processConnection = connection

    if not os.path.exists(dbFileName):
        if createIfNeeded:
            print "Creating database"
            createTables()
            # Set database version according to current yokadi release
            Config(name=DB_VERSION_KEY, value=str(DB_VERSION), system=True, desc="Database schema release number")
        else:
            print "Database file (%s) does not exist or is not readable. Exiting" % dbFileName
            sys.exit(1)

    # Check version
    version = getVersion()
    if version != DB_VERSION:
        tui.error("Your database version is %d but Yokadi wants version %d." \
            % (version, DB_VERSION))
        print "Please, run the update.py script to migrate your database prior to running Yokadi"
        sys.exit(1)

def setDefaultConfig():
    """Set default config parameter in database if they (still) do not exist"""
    defaultConfig={
        "TEXT_WIDTH"      : ("60", False, "Width of task display output with t_list command"),
        "DEFAULT_PROJECT" : ("default", False, "Default project used when no project name given"),
        "ALARM_DELAY_CMD" : ('''kdialog --sorry "task {TITLE} ({ID}) is due for {DATE}" --title "Yokadi Daemon"''',False,
                             "Command executed by Yokadi Daemon when a tasks due date is reached soon (see ALARM_DELAY"),
        "ALARM_DUE_CMD"   : ('''kdialog --error "task {TITLE} ({ID}) should be done now" --title "Yokadi Daemon"''',False,
                             "Command executed by Yokadi Daemon when a tasks due date is reached soon (see ALARM_DELAY"),
        "ALARM_DELAY"     : ("8", False, "Delay (in hours) before due date to launch the alarm (see ALARM_CMD)")}

    for name, value in defaultConfig.items():
        if Config.select(Config.q.name==name).count()==0:
            Config(name=name, value=value[0], system=value[1], desc=value[2])

# vi: ts=4 sw=4 et
