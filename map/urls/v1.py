from django.urls import path
from map.views import (
    MapDetailView,
    MapListView,
    MapPopularDailyListView,
    MapPopularMonthlyListView,
    MapSubscribedListView,
    MyMapListView,
    MapShareLinkView,
    MapShareValidateView, MapFeedbackAnswersView,
)

app_name = 'map'


urlpatterns = [
    path('', MapListView.as_view(), name='map-list'),
    path('/<int:map_id>/share', MapShareLinkView.as_view(), name='map-create-share-link'),
    path('/<int:map_id>/feedback-answers', MapFeedbackAnswersView.as_view(), name='map-feedback-answers'),
    path('/<int:map_id>', MapDetailView.as_view(), name='map-detail'),
    path('/subscribed', MapSubscribedListView.as_view(), name='map-subscribed-list'),
    path('/my', MyMapListView.as_view(), name='my-map-list'),
    path('/popular/daily', MapPopularDailyListView.as_view(), name='map-daily-popular-list'),
    path('/popular/monthly', MapPopularMonthlyListView.as_view(), name='map-monthly-popular-list'),
    path('/share/<int:map_id>', MapShareValidateView.as_view(), name='map-validate-share-link'),
]
