from django.conf.urls import patterns, url, include
from Components.HKP import views

urlpatterns = patterns('',
    (r'lookup$', views.Lookup.as_view()),
)
