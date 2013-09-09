__author__ = 'thospy'

from django.db import models

class Identities(models.Model):

    id = models.CharField(max_length=250)