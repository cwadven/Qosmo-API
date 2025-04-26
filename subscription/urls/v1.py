from django.urls import path

from subscription.views import MapSubscriptionView

app_name = 'subscription'


urlpatterns = [
    path('/map/<int:map_id>', MapSubscriptionView.as_view(), name='map-detail'),
]
