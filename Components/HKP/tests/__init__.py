import unittest
from Components.HKP.tests import models


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(models.PublickeyTest))
    return suite