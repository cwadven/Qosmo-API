from typing import (
    Optional,
    Tuple, Set, List, Dict,
)

from django.db.models import F

from map.models import (
    Arrow,
    Node,
    NodeCompleteRule,
    NodeCompletedHistory, ArrowProgress,
)
from map_graph.dtos.node_detail import NodeDetailDTO, NodeStatisticDTO, NodeCompleteRuleDetailDTO, RuleProgressDTO, \
    QuestionDTO, MyAnswerDTO
from node.exceptions import NodeNotFoundException
from question.consts import QuestionType
from question.models import UserQuestionAnswer


def get_member_completed_question_ids(
        member_id: int,
        question_ids: List[int]
) -> Set[int]:
    if not member_id:
        return set()
    if not question_ids:
        return set()

    return set(
        ArrowProgress.objects.filter(
            arrow__question_id__in=question_ids,
            is_resolved=True,
            member_id=member_id,
        ).values_list(
            'arrow__question_id',
            flat=True,
        )
    )


def get_member_completed_arrow_ids(
        member_id: int,
        arrow_ids: List[int],
) -> Set[int]:
    if not member_id:
        return set()
    if not arrow_ids:
        return set()
    return set(
        ArrowProgress.objects.filter(
            arrow_id__in=arrow_ids,
            is_resolved=True,
            member_id=member_id,
        ).values_list(
            'arrow_id',
            flat=True,
        )
    )


def get_member_completed_node_ids(
        member_id: int,
        node_ids: List[int],
) -> Set[int]:
    if not member_id:
        return set()
    if not node_ids:
        return set()
    return set(
        NodeCompletedHistory.objects.filter(
            member_id=member_id,
            node_id__in=node_ids,
        ).values_list(
            'node_id',
            flat=True,
        )
    )


def find_activatable_node_ids_after_completion(
        member_id: Optional[int],
        node_ids: List[int]
) -> Set[int]:
    """
    현재 Node를 완료하면 in_progress가 되는 Node들을 찾습니다.
    """
    able_to_in_progress_node_ids = set(
        Arrow.objects.filter(
            start_node_id__in=node_ids,
            is_deleted=False,
        ).exclude(
            start_node_id=F('end_node_id'),
        ).values_list(
            'end_node_id',
            flat=True,
        )
    )
    if not member_id:
        return able_to_in_progress_node_ids
    member_node_completed_node_ids = set(
        NodeCompletedHistory.objects.filter(
            member_id=member_id,
            node_id__in=able_to_in_progress_node_ids,
        ).values_list(
            'node_id',
            flat=True,
        )
    )
    return able_to_in_progress_node_ids - member_node_completed_node_ids


class NodeDetailService:
    def __init__(self, member_id: Optional[int] = None):
        self.member_id = member_id

    def get_node_detail(self, node_id: int) -> NodeDetailDTO:
        try:
            node = Node.objects.get(
                id=node_id,
                is_deleted=False,
            )
        except Node.DoesNotExist:
            raise NodeNotFoundException()

        rules = list(
            NodeCompleteRule.objects.filter(
                node_id=node_id,
                is_deleted=False,
            )
        )
        rule_ids = [rule.id for rule in rules]
        arrows = Arrow.objects.filter(
            node_complete_rule_id__in=rule_ids,
            is_deleted=False,
        ).select_related(
            'start_node',
            'question',
        )

        # Rule별 Question 매핑
        questions_by_rule_id = {}
        questions = []
        member_completed_arrow_ids = get_member_completed_arrow_ids(
            self.member_id,
            [arrow.id for arrow in arrows]
        )
        user_question_answers = UserQuestionAnswer.objects.select_related(
            'reviewed_by'
        ).filter(
            member_id=self.member_id,
        ).prefetch_related(
            'files',
        ).order_by(
            '-created_at',
        )
        my_answers_by_question_id = {}
        for user_question_answer in user_question_answers:
            if user_question_answer.question_id not in my_answers_by_question_id:
                my_answers_by_question_id[user_question_answer.question_id] = []
            my_answers_by_question_id[user_question_answer.question_id].append(
                MyAnswerDTO.from_answer(user_question_answer)
            )

        is_start_node = all([arrow.start_node_id == arrow.end_node_id for arrow in arrows])
        for arrow in arrows:
            if arrow.question:
                questions.append(arrow.question)

        member_completed_question_ids = get_member_completed_question_ids(
            self.member_id,
            [question.id for question in questions]
        )
        member_completed_node_ids = get_member_completed_node_ids(
            self.member_id,
            # 현재 노드도 포함
            [arrow.start_node_id for arrow in arrows] + [node_id]
        )
        question_dtos_by_rule_id = {}

        # 현재 조회되는 Node 는 End node
        # Arrows 중에서 completed 된게 하나라도 있으면 in_progress
        # 모든 Arrow 가 start_node_id == end_node_id 면 in_progress
        # 해결된 Node 면 completed
        # 아니면 locked
        node_status = 'locked'
        if node.id in member_completed_node_ids:
            node_status = 'completed'
        elif bool(len({arrow.id for arrow in arrows} & member_completed_arrow_ids)):
            node_status = 'in_progress'
        elif is_start_node:
            node_status = 'in_progress'

        # 통계 데이터 조회
        activated_count, completed_count = self._get_node_statistics(node)
        if node_status == 'locked':
            return NodeDetailDTO(
                id=node.id,
                name=node.name,
                title=node.title,
                description='???',
                status=node_status,
                background_image=None,
                statistic=NodeStatisticDTO(
                    activated_member_count=activated_count,
                    completed_member_count=completed_count,
                ),
                active_rules=[],
            )

        for arrow in arrows:
            if arrow.node_complete_rule_id not in question_dtos_by_rule_id:
                question_dtos_by_rule_id[arrow.node_complete_rule_id] = []

            question_status = 'locked'
            if arrow.question_id in member_completed_question_ids:
                question_status = 'completed'
            elif is_start_node:
                question_status = 'in_progress'
            elif arrow.start_node_id in member_completed_node_ids:
                question_status = 'in_progress'
            # Rule 안에 있에서 통해서 오는 것들이 전부다 해결이 됐어야 문제를 풀수 있도록 해야함
            elif arrow.start_node_id == arrow.end_node_id and node_status == 'in_progress':
                question_status = 'in_progress'

            answer_submittable = bool(self.member_id and question_status == 'in_progress')

            if arrow.question:
                question_dtos_by_rule_id[arrow.node_complete_rule_id].append(
                    # QuestionDTO 안에 문제를 해결할 수 있는 버튼 만들기 혹은 아니기 만들기 (비회원 및 나중을 위해)
                    QuestionDTO(
                        id=arrow.question.id,
                        arrow_id=arrow.id,
                        title=arrow.question.title,
                        description=arrow.question.description,
                        status=question_status,
                        by_node_id=arrow.start_node_id,
                        answer_submit_with_text=QuestionType.TEXT.value in arrow.question.question_types,
                        answer_submit_with_file=QuestionType.FILE.value in arrow.question.question_types,
                        answer_submittable=answer_submittable,
                        my_answers=my_answers_by_question_id.get(arrow.question_id, []),
                    )
                )

                if arrow.node_complete_rule_id not in questions_by_rule_id:
                    questions_by_rule_id[arrow.node_complete_rule_id] = []
                questions_by_rule_id[arrow.node_complete_rule_id].append(arrow.question)
            else:
                question_dtos_by_rule_id[arrow.node_complete_rule_id].append(
                    QuestionDTO(
                        id=None,
                        arrow_id=arrow.id,
                        title=f'"{arrow.start_node.name}"를 완료해주세요.',
                        description=f'"{arrow.start_node.name}" 를 완료해주세요.',
                        status=(
                            'completed'
                            if (arrow.start_node_id in member_completed_node_ids)
                            else 'locked'
                        ),
                        by_node_id=arrow.start_node_id,
                        answer_submit_with_text=False,
                        answer_submit_with_file=False,
                        answer_submittable=answer_submittable,
                        my_answers=[],
                    )
                )

        # Rule 안에 있에서 통해서 오는 것들이 전부다 해결이 됐어야 문제를 풀수 있도록 해야함
        for rule_id, question_dtos in question_dtos_by_rule_id.items():
            is_incoming_node_all_completed = all(
                [
                    question_dto.status == 'completed'
                    for question_dto in question_dtos
                    if question_dto.id is None
                ]
            )
            if not is_incoming_node_all_completed:
                for question_dto in question_dtos:
                    if question_dto.id is not None:
                        question_dto.title = '문제: ???'
                        question_dto.description = '설명: ???'
                        question_dto.status = 'locked'
                        question_dto.answer_submittable = False

        return NodeDetailDTO(
            id=node.id,
            name=node.name,
            title=node.title,
            description=node.description,
            status=node_status,
            background_image=node.background_image,
            statistic=NodeStatisticDTO(
                activated_member_count=activated_count,
                completed_member_count=completed_count,
            ),
            active_rules=[
                NodeCompleteRuleDetailDTO(
                    id=rule.id,
                    name=rule.name,
                    progress=RuleProgressDTO(
                        completed_questions=len(
                            [
                                question_dto
                                for question_dto in question_dtos_by_rule_id.get(rule.id, [])
                                if question_dto.status == 'completed'
                            ]
                        ),
                        total_questions=len(question_dtos_by_rule_id.get(rule.id, [])),
                        percentage=int(
                            len(
                                [
                                    question_dto
                                    for question_dto in question_dtos_by_rule_id.get(rule.id, [])
                                    if question_dto.status == 'completed'
                                ]
                            ) / len(question_dtos_by_rule_id.get(rule.id, [])) * 100
                        )
                        if question_dtos_by_rule_id.get(rule.id, [])
                        else 0,
                    ),
                    questions=question_dtos_by_rule_id.get(rule.id, []),
                )
                for rule in rules
            ],
        )

    def _get_node_statistics(self, node: Node) -> Tuple[int, int]:
        completed_count = self._get_node_completed_member_count(node.id)
        activated_count = self._get_in_progress_member_count(node.id)

        return activated_count, completed_count

    @staticmethod
    def _get_node_completed_member_count(node_id: int) -> int:
        return NodeCompletedHistory.objects.filter(
            node_id=node_id,
        ).values(
            'member',
        ).distinct().count()

    @staticmethod
    def _get_before_node_solved_member_count(node_id: int) -> int:
        # 현재 node_id 의 이전 Node 들을 찾습니다.
        start_node_ids = set(
            Arrow.objects.filter(
                end_node_id=node_id,
            ).values_list(
                'start_node_id',
                flat=True,
            )
        )
        return NodeCompletedHistory.objects.filter(
            node_id__in=start_node_ids,
        ).values(
            'member',
        ).distinct().count()

    def _get_in_progress_member_count(self, node_id: int) -> int:
        return self._get_before_node_solved_member_count(node_id) - self._get_node_completed_member_count(node_id)
