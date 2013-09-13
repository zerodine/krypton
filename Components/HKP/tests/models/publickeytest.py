from django.test import TestCase
from Components.HKP import models

class PublickeyTest(TestCase):
    fixtures = ['publickey.json']
    pub = None

    def setUp(self):
        self.pub = models.Publickey.objects.get(pk="E273AC6458A2DF4F")

    
    def tearDown(self):
        pass

    def test_gpgDetails(self):
        '''{'keyid': u'E273AC6458A2DF4F', 'expires': u'1505023118', 'length': u'4096', 'algo': u'1', 'fingerprint': u'06284050297955B8D37238B0E273AC6458A2DF4F', 'date': u'1378792718', 'type': u'pub'}'''
        details = self.pub.getGpgDetails()
        self.assertDictContainsSubset({'fingerprint': u'06284050297955B8D37238B0E273AC6458A2DF4F'}, details)

    def test_gpgIdentities(self):
        identities = self.pub.getGpgIdentities()
        print identities

    def test_gpgSubkeys(self):
        subkeys = self.pub.getGpgSubkeys()
        print subkeys