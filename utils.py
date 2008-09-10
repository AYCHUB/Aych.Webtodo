# -*- coding: UTF-8 -*-
"""
Misc utilities. Should probably be splitted.

@author: Aurélien Gâteau <aurelien.gateau@free.fr>
@author: Sébastien Renard <sebastien.renard@digitalfox.org>
@license: GPLv3
"""
import sys
import csv
import locale
from datetime import datetime, timedelta
from sqlobject.dberrors import DuplicateEntryError
from sqlobject import AND, LIKE, SQLObjectNotFound
from db import Keyword, Project, Task
import colors as C

# Default user encoding. Used to decode all input strings
# This is a redefinition of yokadi.py ENCODING constant to avoid circular import
ENCODING=locale.getpreferredencoding()

def addTask(projectName, title, keywordDict):
    """Adds a task based on title and keywordDict.
    @param projectName: name of project as a string
    @param title: task title as a string
    @param keywordDict: dictionary of keywords (name : value)
    @returns : Task instance on success, None if cancelled."""
    # Create missing keywords
    if not createMissingKeywords(keywordDict.keys()):
        return None

    # Create missing project
    project = getOrCreateProject(projectName)
    if not project:
        return None

    # Create task
    try:
        task = Task(creationDate = datetime.now(), project=project, title=title, description="", status="new")
        task.setKeywordDict(keywordDict)
    except DuplicateEntryError:
        raise YokadiException("A task named %s already exists in this project. Please find another name" % title)

    return task

def getTaskFromId(line, existingTask=True):
    """Verify that a taskId was provided and optionaly checks if the task exists
    @param line: taskId string
    @param existingTask: wether to check if task really exists
    @return: Task instance or None if existingTask is False"""
    if not line.isdigit():
        raise YokadiException("Provide a task id")
    taskId = int(line)
    if existingTask:
        try:
            task = Task.get(taskId)
        except SQLObjectNotFound:
            raise YokadiException("Task %s does not exist. Use t_list to see all tasks" % taskId)
    else:
        task=None
    return task

#TODO: factorize the two following functions and make a generic one
def getOrCreateKeyword(keywordName, interactive=True):
    """Get a keyword by its name. Create it if needed
    @param keywordName: keyword name as a string
    @param interactive: Ask user before creating keyword (this is the default)
    @type interactive: Bool
    @return: Keyword instance or None if user cancel creation"""
    result = Keyword.selectBy(name=keywordName)
    result = list(result)
    if len(result):
        return result[0]

    while interactive:
        answer = raw_input("Keyword '%s' does not exist, create it (y/n)? " % keywordName)
        if answer == "n":
            return None
        if answer == "y":
            break
    keyword = Keyword(name=keywordName)
    print "Added keyword '%s'" % keywordName
    return keyword


def getOrCreateProject(projectName, interactive=True):
    """Get a project by its name. Create it if needed
    @param projectName: project name as a string
    @param interactive: Ask user before creating project (this is the default)
    @type interactive: Bool
    @return: Project instance or None if user cancel creation"""
    result = Project.selectBy(name=projectName)
    result = list(result)
    if len(result):
        return result[0]

    while interactive:
        answer = raw_input("Project '%s' does not exist, create it (y/n)? " % projectName)
        if answer == "n":
            return None
        if answer == "y":
            break
    project = Project(name=projectName)
    print "Added project '%s'" % projectName
    return project


def createMissingKeywords(lst):
    """Create all keywords from lst which does not exist
    @param lst: list of keyword
    @return: True, if ok, False if user canceled"""
    for keywordName in lst:
        if not getOrCreateKeyword(keywordName):
            return False
    return True

def getItemPropertiesStartingWith(item, field, text):
    """Return a list of item.field starting with text
    @param item: the object item, example : Task, Project, Keyword...
    @param field: the item's field lookup : Project.q.name, Task.q.title, Keyword.q.name. Don't forget the magic q
    @param text: The begining of the text as a str
    @return: list of matching strings"""
    return [x.name for x in item.select(LIKE(field, text + "%"))]

def guessDateFormat(tDate):
    """Guess a date format.
    @param tDate: date string like 30/08/2008 or 30/08 or 30
    @return: date format as a string like %d/%m/%Y or %d/%m or %d"""
    if tDate.count("/")==2:
        fDate="%d/%m/%Y"
    elif tDate.count("/")==1:
        fDate="%d/%m"
    else:
        fDate="%d"
    return fDate

def guessTimeFormat(tTime):
    """Guess a time format.
    @param tTime: time string like 12:30:45 or 12:30 or 12
    @return: time format as a string like %H:%M:%S or %H:%M or %H"""
    if tTime.count(":")==2:
        fTime="%H:%M:%S"
    elif tTime.count(":")==1:
        fTime="%H:%M"
    else:
        fTime="%H"
    return fTime

def formatTimeDelta(timeLeft):
    """Friendly format a time delta :
        - Use fake negative timedelta if needed not to confuse user.
        - Hide seconds when delta > 1 day
        - Hide hours and minutes when delta > 3 days
        - Color time according to time remaining
    @param timeLeft: Remaining time
    @type timeLeft: timedelta (from datetime)
    @return: formated and colored str"""
    if timeLeft < timedelta(0):
        # Negative timedelta are very confusing, so we manually put a "-" and show a positive timedelta
        timeLeft=-timeLeft
        # Shorten timedelta:
        if timeLeft < timedelta(3):
            formatedTimeLeft=shortenTimeDelta(timeLeft, "datetime")
        else:
            formatedTimeLeft=shortenTimeDelta(timeLeft, "date")
        formatedTimeLeft=C.RED+"-"+formatedTimeLeft+C.RESET
    elif timeLeft < timedelta(1):
        formatedTimeLeft=C.PURPLE+str(timeLeft)+C.RESET
    elif timeLeft < timedelta(3):
        formatedTimeLeft=C.ORANGE+shortenTimeDelta(timeLeft, "datetime")+C.RESET
    else:
        formatedTimeLeft=shortenTimeDelta(timeLeft, "date")
    return formatedTimeLeft

def shortenTimeDelta(timeLeft, format):
    """Shorten timeDelta according the format parameter
    @param timeLeft: timedelta to be shorten
    @type timeLeft: timedelta (from datetime)
    @param format: can be "date" (hours, minute and seconds removed) or "datetime" (seconds removed)
    @return: shorten timedelta"""
    if   format=="date":
        return str(timeLeft).split(",")[0]
    elif format=="datetime":
        # Hide seconds (remove the 3 last characters)
        return str(timeLeft)[:-3]

def exportTasks(format, filePath):
    """ to be done """
    # List of exported fields
    fields=["title", "creationDate", "dueDate", "doneDate", "description", "urgency", "status", "project", "keywords"]
    if filePath:
        #TODO: open file with proper encoding
        out=file(filePath, "w")
    else:
        out=sys.stdout
    if  format=="csv":
        csv_writer = csv.writer(out, dialect="excel")
        csv_writer.writerow(fields) # Header
        for task in Task.select():
            row=list(unicode(task.__getattribute__(field)).encode(ENCODING) for field in fields if field!="keywords")
            row.append(", ".join(list(("%s=%s" % k for k in task.getKeywordDict().items())))) # Keywords
            csv_writer.writerow(row)
    elif format=="html":
        print "export in HTML not implemented yet"
    elif format=="xml":
        print "export in XML not implemented yet"
    else:
        raise YokadiException("Unknown format: %s. Use csv, html or xml" % format)

class YokadiException(Exception):
    """Yokadi Exceptions"""
    pass

# vi: ts=4 sw=4 et
