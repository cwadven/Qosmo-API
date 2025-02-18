from django.urls import path
from push.views import DeviceTokenView

app_name = 'push'

urlpatterns = [
    path('/device-token', DeviceTokenView.as_view(), name='device-token'),
]
