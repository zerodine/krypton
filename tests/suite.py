__author__ = 'thospy'

import unittest
from tests import GpgModelTest, JsonParserTest, GpgTest, MassTest, MrParserTest, ReconTest, PublickeyHashTest


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(GpgModelTest.getSuite())
    test_suite.addTest(JsonParserTest.getSuite())
    test_suite.addTest(GpgTest.getSuite())
    test_suite.addTest(MassTest.getSuite())
    test_suite.addTest(MrParserTest.getSuite())
    test_suite.addTest(ReconTest.getSuite())
    test_suite.addTest(PublickeyHashTest.getSuite())

    return test_suite

if __name__ == "__main__":
    #So you can run tests from this package individually.
    TEST_RUNNER = unittest.TextTestRunner()
    TEST_SUITE = suite()
    TEST_RUNNER.run(TEST_SUITE)