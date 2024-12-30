from django.urls import path
from map_graph.views import NodeGraphView

app_name = 'map-graph'

urlpatterns = [
    path('/node/<int:map_id>', NodeGraphView.as_view(), name='node-graph'),
]
