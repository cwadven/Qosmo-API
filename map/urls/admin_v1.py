from django.urls import path
from map.views.admin import (
    get_nodes_by_map,
    get_node_complete_rules_by_map,
    get_questions_by_map,
    get_arrows_by_map,
    get_question_info,
)

app_name = 'map-admin'

urlpatterns = [
    path('/get-nodes-by-map', get_nodes_by_map, name='get-nodes-by-map'),
    path('/get-node-complete-rules-by-map', get_node_complete_rules_by_map, name='get-node-complete-rules-by-map'),
    path('/get-questions-by-map', get_questions_by_map, name='get-questions-by-map'),
    path('/get-arrows-by-map', get_arrows_by_map, name='get-arrows-by-map'),
    path('/get-question-info', get_question_info, name='get-question-info'),
] 