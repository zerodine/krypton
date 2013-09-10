from django.db import models

class Basemodel(models.Model):
    created = models.DateTimeField(auto_now_add = True, null=True, blank=True)
    updated = models.DateTimeField(auto_now_add = True, null=True, blank=True)

    class Meta:
        abstract = True