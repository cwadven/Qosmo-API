from django.urls import path
from map_graph.views import (
    ArrowGraphView,
    NodeGraphView,
)

app_name = 'map-graph'

urlpatterns = [
    path('/node/<int:map_id>', NodeGraphView.as_view(), name='node-graph'),
    path('/arrow/<int:map_id>', ArrowGraphView.as_view(), name='arrow-graph'),
]
