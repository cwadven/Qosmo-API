from django.urls import path
from push.views import DeviceTokenView, TestPushView, PushMapPlayMemberView, PushMapPlayMemberDeleteView, PushMapPlayMemberListView

app_name = 'push'

urlpatterns = [
    path('device-token', DeviceTokenView.as_view(), name='device_token'),
    path('test-push', TestPushView.as_view(), name='test_push'),
    path('map-play-member/<int:map_play_member_id>', PushMapPlayMemberView.as_view(), name='push_map_play_member'),
    path('push-map-play-member/<int:push_map_play_member_id>', PushMapPlayMemberDeleteView.as_view(), name='push_map_play_member_delete'),
    path('map-play-member/<int:map_play_member_id>/push-settings', PushMapPlayMemberListView.as_view(), name='push_map_play_member_list'),
]
