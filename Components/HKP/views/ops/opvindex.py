from django.http import HttpResponse
from Components.HKP.views.ops import OpAbstractBase

class OpVindex(OpAbstractBase):

    def do(self, search = None, options = [], fingerprint = False, exact = False):
        return HttpResponse("-".join(options))