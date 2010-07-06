# -*- coding: UTF-8 -*-
"""
Task test cases
@author: Aurélien Gâteau <aurelien.gateau@free.fr>
@author: Sébastien Renard <sebastien.renard@digitalfox.org>
@license: GPL v3 or later
"""
import sys
import unittest
from StringIO import StringIO

import testutils

import tui
from db import Task
from yokadi import YokadiCmd
from yokadiexception import YokadiException, BadUsageException

class TaskTestCase(unittest.TestCase):
    def setUp(self):
        testutils.clearDatabase()
        tui.clearInputAnswers()
        self.cmd = YokadiCmd()

    def testAdd(self):
        tui.addInputAnswers("y")
        self.cmd.do_t_add("x t1")

        tui.addInputAnswers("y", "y")
        self.cmd.do_t_add("x @kw1 @kw2=12 t2")

        tui.addInputAnswers("n")
        self.cmd.do_t_add("notExistingProject newTask")

        tasks = list(Task.select())
        result = [x.title for x in tasks]
        expected = [u"t1", u"t2"]
        self.assertEqual(result, expected)

        kwDict = Task.get(2).getKeywordDict()
        self.assertEqual(kwDict, dict(kw1=None, kw2=12))

        for bad_input in ("", # No project
                          "x"): # No task name
            self.assertRaises(BadUsageException, self.cmd.do_t_add, bad_input)

        # Existing task
        self.assertRaises(YokadiException, self.cmd.do_t_add, "x t1")

    def testMark(self):
        tui.addInputAnswers("y")
        self.cmd.do_t_add("x t1")
        task = Task.get(1)
        self.assertEqual(task.status, "new")
        self.cmd.do_t_mark_started("1")
        self.assertEqual(task.status, "started")
        self.cmd.do_t_mark_done("1")
        self.assertEqual(task.status, "done")

    def testAddKeywords(self):
        tui.addInputAnswers("y")
        self.cmd.do_t_add("x t1")
        task = Task.get(1)

        tui.addInputAnswers("y", "y")
        self.cmd.do_t_add_keywords("1 @kw1 @kw2=12")

        kwDict = task.getKeywordDict()
        self.assertEqual(kwDict, dict(kw1=None, kw2=12))

        for bad_input in ("", # No task
                          "1", # No keyword
                          "1 kw1"): # No @ before kw1
            self.assertRaises(YokadiException, self.cmd.do_t_add_keywords, bad_input)

    def testLastTaskId(self):
        # Using "_" with no prior task activity should raise an exception   
        self.assertRaises(YokadiException, self.cmd.getTaskFromId, "_")

        tui.addInputAnswers("y")
        self.cmd.do_t_add("x t1")
        task1 = Task.get(1)
        self.assertEqual(self.cmd.getTaskFromId("_"), task1)

        self.cmd.do_t_add("x t2")
        task2 = Task.get(2)
        self.assertEqual(self.cmd.getTaskFromId("_"), task2)

        self.cmd.do_t_mark_started("1")
        self.assertEqual(self.cmd.getTaskFromId("_"), task1)

    def testRecurs(self):
        tui.addInputAnswers("y")
        self.cmd.do_t_add("x t1")
        task = Task.get(1)
        self.cmd.do_t_recurs("1 daily 10:00")
        desc = str(task.recurrence)
        self.cmd.do_t_recurs("1 weekly FR 23:00")
        self.cmd.do_t_recurs("1 none")
        self.cmd.do_t_recurs("1 weekly fr 23:00")
        self.cmd.do_t_recurs("1 weekly Fr 23:00")
        self.cmd.do_t_recurs("1 weekly Friday 23:00")
        self.cmd.do_t_recurs("1 monthly 3 13:00")
        self.cmd.do_t_recurs("1 monthly second friday 13:00")
        self.cmd.do_t_recurs("1 yearly 3/07 11:20")
        self.cmd.do_t_recurs("1 quarterly 14 11:20")
        self.cmd.do_t_recurs("1 quarterly first monday 23:20")
        self.assertNotEqual(desc, str(task.recurrence))
        self.assertEqual(task.status, "new")
        self.cmd.do_t_mark_done("1")
        self.assertEqual(task.status, "new")

        for bad_input in ("", # No task
                          "1", # No recurence
                          "1 foo", # Unknown recurrence
                          "1 daily", # No time
                          "1 weekly", # No day
                          "1 weekly monday", # No time
                          "1 monthly", # No day
                          "1 monthly 10", # No time
                          "1 quarterly", # No day
                          "1 quarterly 10", # No time
                          "1 monthly foo 12:00", # Bad date
                          ):
            self.assertRaises(YokadiException, self.cmd.do_t_recurs, bad_input)

    def testTlist(self):
        tui.addInputAnswers("y")
        self.cmd.do_t_add("x t1")
        tui.addInputAnswers("y", "y")
        self.cmd.do_t_add("x @kw1 @kw2=12 t2")

        for line in ("", "-a", "-t", "-d today", "-u 10", "-k %", "-k _%", "-s t", "--overdue",
                     "@%", "@k%", "!@%", "!@kw1", "-f plain", "-f xml", "-f html"):
            self.cmd.do_t_list(line)

    def testTfilter(self):
        tui.addInputAnswers("y")
        self.cmd.do_t_add("x t1")
        tui.addInputAnswers("y", "y")
        self.cmd.do_t_add("x @kw1 @kw2=12 t2")
        tui.addInputAnswers("y")
        self.cmd.do_t_add("y t3")

        for filter in ("@kw1", "x", "x @kw1", "none"):
            self.cmd.do_t_filter(filter)
            out = StringIO()
            oldstdout = sys.stdout
            tui.stdout = out
            self.cmd.do_t_list("")
            self.assertTrue("t2" in out.getvalue())
            if filter in ("x", "none"):
                self.assertTrue("t1" in out.getvalue())
            else:
                self.assertFalse("t1" in out.getvalue())
            if filter == "none":
                self.assertTrue("t3" in out.getvalue())
            else:
                self.assertFalse("t3" in out.getvalue())

            tui.stdout = oldstdout

        self.assertRaises(YokadiException, self.cmd.do_t_filter, "")
# vi: ts=4 sw=4 et
