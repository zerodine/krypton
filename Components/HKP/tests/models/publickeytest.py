from django.test import TestCase
from Components.HKP import models

class PublickeyTest(TestCase):
    fixtures = ['publickey.json']

    def setUp(self):
        #self.leasing = Leasing()
        pass
    
    def tearDown(self):
        pass

    def test_gpgDetails(self):
        pub = models.Publickey.objects.get(pk="E273AC6458A2DF4F")
        print pub.getDetails()