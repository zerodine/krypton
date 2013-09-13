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

    def syncKeyWithModel(self):
        g = Gpg()
        g.loadPublicKey(asciiarmoredkey=self.gpgdata)
        details = g.getKeydetails()
        subkeys = g.getSubkeys()
        identities = g.getIdentities()

    def getGpgDetails(self):
        g = Gpg()
        g.loadPublicKey(asciiarmoredkey=self.gpgdata)
        return g.getKeydetails()

    def getGpgSubkeys(self):
        g = Gpg()
        g.loadPublicKey(asciiarmoredkey=self.gpgdata)
        return g.getSubkeys()

    def getGpgIdentities(self):
        g = Gpg()
        g.loadPublicKey(asciiarmoredkey=self.gpgdata)
        return g.getIdentities()

    def __unicode__(self):
        return self.keyid
