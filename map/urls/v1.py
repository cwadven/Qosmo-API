from django.urls import path
from map.views import (
    MapDetailView,
    MapListView,
)

app_name = 'map'


urlpatterns = [
    path('', MapListView.as_view(), name='map-list'),
    path('/<int:map_id>', MapDetailView.as_view(), name='map-detail'),
    path('/subscribed', MapListView.as_view(), name='map-subscribed-list'),
]
