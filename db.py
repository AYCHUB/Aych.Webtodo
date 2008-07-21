from sqlobject import *

class Project(SQLObject):
    class sqlmeta:
        defaultOrder = "name"
    name = UnicodeCol(alternateID=True, notNone=True)


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
    title = UnicodeCol(alternateID=True)
    creationDate = DateTimeCol(notNone=True)
    description = UnicodeCol(default="", notNone=True)
    urgency = IntCol(default=0, notNone=True)
    status = EnumCol(enumValues=['new', 'started', 'done'])
    project = ForeignKey("Project")
    keywords = RelatedJoin("Keyword",
        createRelatedTable=False,
        intermediateTable="task_keyword",
        joinColumn="task_id",
        otherColumn="keyword_id")

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


def createTables():
    Project.createTable()
    Keyword.createTable()
    Task.createTable()
    TaskKeyword.createTable()
# vi: ts=4 sw=4 et
