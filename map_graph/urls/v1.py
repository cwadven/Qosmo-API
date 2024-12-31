from django.urls import path
from map_graph.views import (
    ArrowGraphView,
    NodeGraphView,
    NodeCompleteRuleView,
)

app_name = 'map-graph'

urlpatterns = [
    path('/node/<int:map_id>', NodeGraphView.as_view(), name='node-graph'),
    path('/arrow/<int:map_id>', ArrowGraphView.as_view(), name='arrow-graph'),
    path('/node-complete-rule/<int:map_id>', NodeCompleteRuleView.as_view(), name='node-complete-rule'),
]
