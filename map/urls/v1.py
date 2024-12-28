from django.urls import path
from map.views import MapListView

app_name = 'map'


urlpatterns = [
    path('', MapListView.as_view(), name='map-list'),
]
