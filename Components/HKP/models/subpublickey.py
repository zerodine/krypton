__author__ = 'thospy'

from django.db import models
from Components.HKP.models import Basemodel, Publickey

class Subpublickey(Basemodel):
    class Meta:
        app_label = 'HKP'

    keyid = models.CharField(max_length=18, unique=True, primary_key=True)
    publickey = models.ForeignKey(Publickey)

    def __unicode__(self):
        return self.keyid
