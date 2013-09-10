__author__ = 'thospy'

from django.db import models
from Components.HKP.models import Basemodel
from libs.gpg import Gpg

class Publickey(Basemodel):
    class Meta:
        app_label = 'HKP'

    keyid = models.CharField(max_length=18, unique=True, primary_key=True)
    gpgdata = models.TextField()
    fingerprint = models.CharField(max_length=250)

    def getDetails(self):
        g = Gpg()
        g.loadPublicKey(asciiarmoredkey=self.gpgdata)
        return g.getKeydetails()


    def __unicode__(self):
        return self.keyid
