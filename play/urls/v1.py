from django.urls import path
from play.views import (
    MapPlayCreateView,
    MapPlayInviteCodeView,
    MapPlayJoinView,
    MapPlayMemberRoleView,
    MapPlayMemberBanView,
)


urlpatterns = [
    path('/map/<int:map_id>', MapPlayCreateView.as_view(), name='map-play-create'),
    path('/plays/<int:map_play_id>/invite-codes', MapPlayInviteCodeView.as_view(), name='map-play-invite-codes'),
    path('/plays/join/<str:code>', MapPlayJoinView.as_view(), name='map-play-join'),
    path('/plays/<int:map_play_id>/members/<int:member_id>/role', MapPlayMemberRoleView.as_view(), name='map-play-member-role'),
    path('/plays/<int:map_play_id>/members/<int:member_id>/ban', MapPlayMemberBanView.as_view(), name='map-play-member-ban'),
]
