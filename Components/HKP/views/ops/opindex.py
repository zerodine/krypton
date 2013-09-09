from django.http import HttpResponse
from Components.HKP.views.ops import OpAbstractBase

class OpIndex(OpAbstractBase):

    def do(self, search = None, options = [], fingerprint = False, exact = False):
        return HttpResponse("-".join(options))