__author__ = 'thospy'

import unittest
from tests import GpgModelTest, JsonParserTest


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(GpgModelTest.getSuite())
    test_suite.addTest(JsonParserTest.getSuite())
    return test_suite

if __name__ == "__main__":
    #So you can run tests from this package individually.
    TEST_RUNNER = unittest.TextTestRunner()
    TEST_SUITE = suite()
    TEST_RUNNER.run(TEST_SUITE)