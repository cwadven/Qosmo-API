from django.urls import path
from push.views import DeviceTokenView, TestPushView

app_name = 'push'

urlpatterns = [
    path('/device-token', DeviceTokenView.as_view(), name='device-token'),
    path('/test', TestPushView.as_view(), name='test-push'),
]
