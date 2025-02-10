from django.urls import path
from map_graph.views import (
    ArrowGraphView,
    NodeGraphView,
    NodeCompleteRuleView,
    MapMetaView,
)

app_name = 'map-graph'

urlpatterns = [
    path('/node/<int:map_id>', NodeGraphView.as_view(), name='node-graph'),
    path('/node/<int:map_id>/member_play/<int:map_play_member_id>', NodeGraphView.as_view(), name='node-graph-with-map-play-member'),
    path('/arrow/<int:map_id>', ArrowGraphView.as_view(), name='arrow-graph'),
    path('/arrow/<int:map_id>/member_play/<int:map_play_member_id>', ArrowGraphView.as_view(), name='arrow-graph-with-map-play-member'),
    path('/node-complete-rule/<int:map_id>', NodeCompleteRuleView.as_view(), name='node-complete-rule'),
    path('/meta/<int:map_id>', MapMetaView.as_view(), name='map-meta'),
    path('/meta/<int:map_id>/member_play/<int:map_play_member_id>', MapMetaView.as_view(), name='map-meta-with-map-play-member'),
]
