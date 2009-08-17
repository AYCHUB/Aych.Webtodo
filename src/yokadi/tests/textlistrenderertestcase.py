# -*- coding: UTF-8 -*-
"""
TextListRenderer test cases
@author: Aurélien Gâteau <aurelien.gateau@free.fr>
@license: GPLv3
"""

import unittest
from StringIO import StringIO

import colors as C
import dbutils
import testutils

import tui
from textlistrenderer import TextListRenderer

class TextListRendererTestCase(unittest.TestCase):
    def setUp(self):
        testutils.clearDatabase()
        tui.clearInputAnswers()

    def testTitleFormater(self):
        dbutils.getOrCreateProject("x", interactive=False)
        dbutils.getOrCreateKeyword("k1", interactive=False)
        dbutils.getOrCreateKeyword("k2", interactive=False)
        t1 = dbutils.addTask("x", "t1", {})
        t2 = dbutils.addTask("x", "t2", {"k1":None, "k2":12})

        out = StringIO()
        renderer = TextListRenderer(out, termWidth=80)
        renderer.addTaskList("Foo", [t1])
        renderer.end()
        expected=(u"\n" \
            + "%(CYAN)s              Foo               %(RESET)s\n" \
            + "%(BOLD)sID|Title|U  |S|Age     |Due date%(RESET)s\n" \
            +         "--------------------------------\n" \
            +         "1 |t1   |0  |N|0m      |        \n" \
            )% dict(CYAN=C.CYAN, RESET=C.RESET, BOLD=C.BOLD)
        testutils.multiLinesAssertEqual(self, out.getvalue(), expected)

        longerTask = dbutils.addTask("x", "A longer task name", {})

        out = StringIO()
        renderer = TextListRenderer(out, termWidth=80)
        renderer.addTaskList("Foo", [longerTask])
        renderer.end()
        expected=(u"\n" \
            + "%(CYAN)s                     Foo                      %(RESET)s\n" \
            + "%(BOLD)sID|Title              |U  |S|Age     |Due date%(RESET)s\n" \
            +         "----------------------------------------------\n" \
            +         "3 |A longer task name |0  |N|0m      |        \n" \
            )% dict(CYAN=C.CYAN, RESET=C.RESET, BOLD=C.BOLD)
        testutils.multiLinesAssertEqual(self, out.getvalue(), expected)


# vi: ts=4 sw=4 et
