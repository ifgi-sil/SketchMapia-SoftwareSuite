from django.urls import path
from . import views

app_name = 'generalizingmaps'
urlpatterns = [
    path('fetch_data/', views.fetch_data, name='overpassapi'),
    path('omission_deadend/', views.omission_deadendstreets),
    path('mmReceiver/',views.mmGeoJsonReceiver),
    path('smReceiver/',views.smGeoJsonReceiver),
    path('analyzeInputMap/',views.analyzeInputMap),
    path('requestFME/',views.requestFME),
    path('', views.map, name='map'),
]