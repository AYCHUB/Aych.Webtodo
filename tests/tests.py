import sys
import unittest

sys.path.append("..")
import parseutils

gTaskLineToParsedStructList = [
    ("project some text -k keyword1 -k keyword2=12 some other text", ("project", "some text some other text", {"keyword1":None, "keyword2":12} )),
    ]

class ParseUtilsTests(unittest.TestCase):
    def testExtractKeywords(self):
        for src, dst in gTaskLineToParsedStructList:
            result = parseutils.parseTaskLine(src)
            self.assertEqual(result, dst)

    def testCreateTaskLine(self):
        for dummy, parsedStruct in gTaskLineToParsedStructList:
            # We do not check the result of createTaskLine() against the
            # original task line because there are many ways to write the same
            # taskLine.
            taskLine = parseutils.createTaskLine(*parsedStruct)
            result = parseutils.parseTaskLine(taskLine)
            self.assertEqual(result, parsedStruct)



if __name__ == "__main__":
    unittest.main()
# vi: ts=4 sw=4 et
