from django.urls import path
from map.views import (
    MapDetailView,
    MapListView,
    MapSubscribedListView,
)

app_name = 'map'


urlpatterns = [
    path('', MapListView.as_view(), name='map-list'),
    path('/<int:map_id>', MapDetailView.as_view(), name='map-detail'),
    path('/subscribed', MapSubscribedListView.as_view(), name='map-subscribed-list'),
]
