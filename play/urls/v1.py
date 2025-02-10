from django.urls import path
from play.views import (
    MapPlayInviteCodeView,
    MapPlayJoinView,
    MapPlayMemberRoleView,
    MapPlayMemberBanView,
    MapPlayView,
)


urlpatterns = [
    path('/map/<int:map_id>', MapPlayView.as_view(), name='map-play-create'),
    path('/<int:map_play_id>/invite-codes', MapPlayInviteCodeView.as_view(), name='map-play-invite-codes'),
    path('/join/<str:code>', MapPlayJoinView.as_view(), name='map-play-join'),
    path('/<int:map_play_id>/members/<int:member_id>/role', MapPlayMemberRoleView.as_view(), name='map-play-member-role'),
    path('/<int:map_play_id>/members/<int:member_id>/ban', MapPlayMemberBanView.as_view(), name='map-play-member-ban'),
]
