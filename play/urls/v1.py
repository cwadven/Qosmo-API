from django.urls import path
from play.views import (
    MapPlayInviteCodeView,
    MapPlayJoinView,
    MapPlayMemberRoleView,
    MapPlayMemberBanView,
    MapPlayView,
    MapPlayMemberSelfDeactivateView,
    MapPlayMemberListView,
)


urlpatterns = [
    path('/map/<int:map_id>', MapPlayView.as_view(), name='map-play-create'),
    path('/<int:map_play_member_id>/invite-codes', MapPlayInviteCodeView.as_view(), name='map-play-invite-codes'),
    path('/join/<str:code>', MapPlayJoinView.as_view(), name='map-play-join'),
    path('/<int:map_play_member_id>/member/role', MapPlayMemberRoleView.as_view(), name='map-play-member-role'),
    path('/<int:map_play_member_id>/member/ban', MapPlayMemberBanView.as_view(), name='map-play-member-ban'),
    path('/<int:map_play_member_id>/member/self-deactivate', MapPlayMemberSelfDeactivateView.as_view(), name='map-play-member-self-deactivate'),
    path('/<int:map_play_member_id>/members', MapPlayMemberListView.as_view(), name='map-play-member-list'),
]
