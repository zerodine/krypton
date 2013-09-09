from django.http import HttpResponse
from django.http import Http404
from django.views.generic.base import View

from Components.HKP.views import ops

class Lookup(View):

    def get(self, request):
        opstr = str(request.GET.get('op')).lower()
        op = None

        if opstr == "index":
            op = ops.OpIndex()
        elif opstr == "vindex":
            op = ops.OpVindex()
        elif opstr == "get":
            op = ops.OpGet()

        if not op:
            raise Http404

        return HttpResponse(op.do(
            search=request.GET.get('search'),
            options=str(request.GET.get('options')).split(','),
            #fingerprint=request.GET.get('search'),
            #exact=request.GET.get('search'),
        ))