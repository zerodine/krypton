__author__ = 'thospy'

from django.db import models
from Components.HKP.models import Publickey, Basemodel

class Identity(Basemodel):
    class Meta:
        app_label = 'HKP'

    uid = models.CharField(max_length=250)
    publickey = models.ForeignKey(Publickey)

    def __unicode__(self):
        return self.uid