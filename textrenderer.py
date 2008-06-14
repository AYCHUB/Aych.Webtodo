TASK_LIST_FORMAT="%(id)-3s|%(title)-60s|%(urgency)-3s|%(status)-1s|%(creationDate)-19s"

class TextRenderer(object):
    def renderTaskListHeader(self):
        line = TASK_LIST_FORMAT % dict(id="ID", title="Title", urgency="U", status="S", creationDate="Date")
        print line
        print "-" * len(line)


    def renderTaskListRow(self, task):
        title = task.title
        hasDescription = task.description != ""
        maxLength = 60
        if hasDescription:
            maxLength -=1
        if len(title) > maxLength:
            title = title[:maxLength - 1] + ">"
        if hasDescription:
            title = title.ljust(maxLength) + "*"

        status = task.status[0].upper()
        creationDate = task.creationDate
        urgency = int(task.urgency)

        print TASK_LIST_FORMAT % dict(id=str(task.id), title=title, urgency=urgency, status=status, creationDate=creationDate)


    def renderTaskDetails(self, task):
        propertyDict = task.getPropertyDict()
        propertyArray = []
        for name, value in propertyDict.items():
            txt = name
            if value:
                txt += "=" + str(value)
            propertyArray.append(txt)
            propertyArray.sort()
        properties = ", ".join(propertyArray)
        fields = [
            ("Title", task.title),
            ("Created", task.creationDate),
            ("Status", task.status),
            ("Properties", properties),
            ]

        maxWidth = max([len(x) for x,y in fields])
        format="%" + str(maxWidth) + "s: %s"
        for caption, value in fields:
            print format % (caption, value)

        if task.description != '':
            print
            print task.description
