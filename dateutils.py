# -*- coding: UTF-8 -*-
"""
Date utilities.

@author: Sébastien Renard <sebastien.renard@digitalfox.org>
@license: GPLv3
"""
import time
from datetime import datetime, timedelta

import colors as C
from yokadiexception import YokadiException


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


def parseHumaneDateTime(line):
    # Date & Time format
    fDate=None
    fTime=None

    today=datetime.today().replace(microsecond=0)

    # Initialise dueDate to now (may be now + fixe delta ?)
    dueDate=today # Safe because datetime objects are immutables

    if line.startswith("+"):
        #Delta/relative date and/or time
        line=line.upper().strip("+")
        try:
            if   line.endswith("W"):
                dueDate=today+timedelta(days=float(line[0:-1])*7)
            elif line.endswith("D"):
                dueDate=today+timedelta(days=float(line[0:-1]))
            elif line.endswith("H"):
                dueDate=today+timedelta(hours=float(line[0:-1]))
            elif line.endswith("M"):
                dueDate=today+timedelta(minutes=float(line[0:-1]))
            else:
                raise YokadiException("Unable to understand time shift. See help t_set_due")
        except ValueError:
            raise YokadiException("Timeshift must be a float or an integer")
    else:
        #Absolute date and/or time
        if " " in line:
            # We assume user give date & time
            tDate, tTime=line.split()
            fDate=guessDateFormat(tDate)
            fTime=guessTimeFormat(tTime)
            try:
                dueDate=datetime(*time.strptime(line, "%s %s" % (fDate, fTime))[0:5])
            except Exception, e:
                raise YokadiException("Unable to understand date & time format:\t%s" % e)
        else:
            if ":" in line:
                fTime=guessTimeFormat(line)
                try:
                    tTime=datetime(*time.strptime(line, fTime)[0:5]).time()
                except ValueError:
                    raise YokadiException("Invalid time format")
                dueDate=datetime.combine(today, tTime)
            else:
                fDate=guessDateFormat(line)
                try:
                    dueDate=datetime(*time.strptime(line, fDate)[0:5])
                except ValueError:
                    raise YokadiException("Invalid date format")
        if fDate:
            # Set year and/or month to current date if not given
            if not "%Y" in fDate:
                dueDate=dueDate.replace(year=today.year)
            if not "%M" in fDate:
                dueDate=dueDate.replace(month=today.month)

    return dueDate


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
# vi: ts=4 sw=4 et
