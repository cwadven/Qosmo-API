from django.urls import path

from node.views import NodeDetailView

app_name = 'node'


urlpatterns = [
    path('/<int:node_id>', NodeDetailView.as_view(), name='node-detail'),
]
