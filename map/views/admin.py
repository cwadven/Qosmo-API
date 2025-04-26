from django.db.models import F
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_GET

from map.models import Node, NodeCompleteRule, Map, Arrow
from question.models import Question


@staff_member_required
@require_GET
def get_nodes_by_map(request):
    """맵 ID에 해당하는 노드 목록을 반환합니다."""
    map_id = request.GET.get('map_id')
    if not map_id:
        return JsonResponse([])
    
    nodes = Node.objects.filter(map_id=map_id, is_deleted=False).values('id', 'name')
    return JsonResponse(list(nodes), safe=False)


@staff_member_required
@require_GET
def get_node_complete_rules_by_map(request):
    """맵 ID에 해당하는 노드 완료 규칙 목록을 반환합니다."""
    map_id = request.GET.get('map_id')
    if not map_id:
        return JsonResponse([])
    
    rules = NodeCompleteRule.objects.filter(map_id=map_id, is_deleted=False).values('id', 'name')
    return JsonResponse(list(rules), safe=False)


@staff_member_required
@require_GET
def get_questions_by_map(request):
    """맵 ID에 해당하는 문제 목록을 반환합니다."""
    map_id = request.GET.get('map_id')
    if not map_id:
        return JsonResponse([])
    
    questions = Question.objects.filter(map_id=map_id, is_deleted=False).values('id', 'title')
    return JsonResponse(list(questions), safe=False)


@staff_member_required
@require_GET
def get_arrows_by_map(request):
    """맵 ID에 해당하는 화살표 목록을 반환합니다."""
    map_id = request.GET.get('map_id')
    same_node = request.GET.get('same_node', 'false').lower() == 'true'
    if not map_id:
        return JsonResponse([])

    arrow_qs = Arrow.objects.filter(map_id=map_id, is_deleted=False)
    if same_node:
        arrow_qs = arrow_qs.filter(
            start_node_id=F('node_complete_rule__node_id')
        )
    arrows = arrow_qs.values('id', 'start_node__name')
    
    # start_node__name을 name 필드로 변환
    result = []
    for arrow in arrows:
        result.append({
            'id': arrow['id'],
            'name': f"Start: {arrow['start_node__name']}" if arrow['start_node__name'] else f"Arrow ID: {arrow['id']}"
        })
    
    return JsonResponse(result, safe=False)


@staff_member_required
@require_GET
def get_question_info(request):
    """질문 ID에 해당하는 질문 정보를 반환합니다."""
    question_id = request.GET.get('question_id')
    if not question_id:
        return JsonResponse({})
    
    try:
        question = Question.objects.select_related('map').get(id=question_id, is_deleted=False)
        
        result = {
            'id': question.id,
            'title': question.title,
            'description': question.description,
            'question_types': question.question_types,
            'map_id': question.map_id,
            'map_name': question.map.name if question.map else None,
        }
        
        return JsonResponse(result)
    except Question.DoesNotExist:
        return JsonResponse({'error': '질문을 찾을 수 없습니다.'}, status=404) 