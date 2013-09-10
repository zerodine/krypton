__author__ = 'thospy'

from django.db import models
from Components.HKP.models import Basemodel

class Keyserver(Basemodel):
    class Meta:
        app_label = 'HKP'

    server = models.CharField(max_length=250, unique=True)

    def __unicode__(self):
        return self.server
