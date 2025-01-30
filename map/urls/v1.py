from django.urls import path
from map.views import (
    MapDetailView,
    MapListView,
    MapSubscribedListView, MapPopularMonthlyListView, MapPopularDailyListView,
)

app_name = 'map'


urlpatterns = [
    path('', MapListView.as_view(), name='map-list'),
    path('/<int:map_id>', MapDetailView.as_view(), name='map-detail'),
    path('/subscribed', MapSubscribedListView.as_view(), name='map-subscribed-list'),
    path('/popular/daily', MapPopularDailyListView.as_view(), name='map-daily-popular-list'),
    path('/popular/monthly', MapPopularMonthlyListView.as_view(), name='map-monthly-popular-list'),
]
