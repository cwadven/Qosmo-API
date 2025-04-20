from typing import (
    List,
    Optional,
    Tuple,
    Set,
)

from django.db.models import F, Q, Case, When, Value, IntegerField

from map.models import (
    Arrow,
    ArrowProgress,
    Node,
    NodeCompleteRule,
    NodeCompletedHistory,
)
from map_graph.dtos.node_detail import (
    FileDTO,
    MyAnswerDTO,
    NodeCompleteRuleDetailDTO,
    NodeDetailDTO,
    NodeStatisticDTO,
    QuestionDTO,
    RuleProgressDTO,
)
from node.exceptions import NodeNotFoundException
from play.models import MapPlayMember
from question.consts import QuestionType
from question.models import (
    QuestionFile,
    UserQuestionAnswer,
)
from subscription.services.subscription_service import MapSubscriptionService


def get_map_play_member_completed_question_ids(
        map_play_member_id: Optional[int],
        question_ids: List[int]
) -> Set[int]:
    if not map_play_member_id:
        return set()
    if not question_ids:
        return set()

    return set(
        ArrowProgress.objects.filter(
            arrow__question_id__in=question_ids,
            is_resolved=True,
            map_play_member_id=map_play_member_id,
        ).values_list(
            'arrow__question_id',
            flat=True,
        )
    )


def get_map_play_completed_question_ids(
        map_play_id: Optional[int],
        question_ids: List[int]
) -> Set[int]:
    if not map_play_id:
        return set()
    if not question_ids:
        return set()

    return set(
        ArrowProgress.objects.filter(
            arrow__question_id__in=question_ids,
            is_resolved=True,
            map_play_member__map_play_id=map_play_id,
        ).values_list(
            'arrow__question_id',
            flat=True,
        )
    )


def get_map_play_member_completed_arrow_ids(
        map_play_member_id: int,
        arrow_ids: List[int],
) -> Set[int]:
    if not map_play_member_id:
        return set()
    if not arrow_ids:
        return set()
    return set(
        ArrowProgress.objects.filter(
            arrow_id__in=arrow_ids,
            is_resolved=True,
            map_play_member_id=map_play_member_id,
        ).values_list(
            'arrow_id',
            flat=True,
        )
    )


def get_map_play_completed_arrow_ids(
        map_play_id: Optional[int],
        arrow_ids: List[int],
) -> Set[int]:
    if not map_play_id:
        return set()
    if not arrow_ids:
        return set()
    return set(
        ArrowProgress.objects.filter(
            arrow_id__in=arrow_ids,
            is_resolved=True,
            map_play_member__map_play_id=map_play_id,
        ).values_list(
            'arrow_id',
            flat=True,
        )
    )


def get_map_play_member_completed_node_ids(
        map_play_member_id: int,
        node_ids: List[int],
) -> Set[int]:
    if not map_play_member_id:
        return set()
    if not node_ids:
        return set()
    return set(
        NodeCompletedHistory.objects.filter(
            map_play_member_id=map_play_member_id,
            node_id__in=node_ids,
        ).values_list(
            'node_id',
            flat=True,
        )
    )


def get_map_play_completed_node_ids(
        map_play_id: Optional[int],
        node_ids: List[int],
) -> Set[int]:
    if not map_play_id:
        return set()
    if not node_ids:
        return set()
    return set(
        NodeCompletedHistory.objects.filter(
            map_play_member__map_play_id=map_play_id,
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
            start_node_id=F('node_complete_rule__node_id'),
        ).values_list(
            'node_complete_rule__node_id',
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
    def __init__(self, member_id: Optional[int] = None, map_play_member_id: Optional[int] = None):
        self.member_id = member_id
        self.map_play_member = (
            MapPlayMember.objects.select_related(
                'map_play',
            ).filter(
                id=map_play_member_id,
            ).first()
            if map_play_member_id else None
        )
        self.map_play = self.map_play_member.map_play if self.map_play_member else None

    @property
    def map_play_member_id(self):
        return self.map_play_member.id if self.map_play_member else None

    @property
    def map_play_id(self):
        return self.map_play.id if self.map_play else None

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
        members_completed_arrow_ids = get_map_play_completed_arrow_ids(
            self.map_play_id,
            [arrow.id for arrow in arrows]
        )
        users_question_answers = UserQuestionAnswer.objects.select_related(
            'reviewed_by',
            'member',
        ).filter(
            Q(map_play_member_id=self.map_play_member_id) | Q(is_correct=True),
        ).prefetch_related(
            'files',
        ).annotate(
            is_correct_order=Case(
                When(is_correct=True, then=Value(0)),
                When(is_correct=None, then=Value(1)),
                When(is_correct=False, then=Value(2)),
                output_field=IntegerField(),
            )
        ).order_by(
            'is_correct_order',
            '-created_at',
        )
        users_answers_by_question_id = {}
        for users_question_answer in users_question_answers:
            if users_question_answer.question_id not in users_answers_by_question_id:
                users_answers_by_question_id[users_question_answer.question_id] = []
            users_answers_by_question_id[users_question_answer.question_id].append(
                MyAnswerDTO.from_answer(users_question_answer)
            )

        is_start_node = all([arrow.start_node_id == arrow.end_node_id for arrow in arrows])
        for arrow in arrows:
            if arrow.question:
                questions.append(arrow.question)

        question_ids = [question.id for question in questions]
        members_completed_question_ids = get_map_play_completed_question_ids(
            self.map_play_id,
            question_ids
        )
        members_completed_node_ids = get_map_play_completed_node_ids(
            self.map_play_id,
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
        if not node.is_active:
            node_status = 'deactivated'
        elif node.id in members_completed_node_ids:
            node_status = 'completed'
        elif bool(len({arrow.id for arrow in arrows} & members_completed_arrow_ids)):
            node_status = 'in_progress'
        elif is_start_node:
            node_status = 'in_progress'

        # 통계 데이터 조회
        activated_count, completed_count = self._get_node_map_play_statistics(node)
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

        subscription_service = MapSubscriptionService(member_id=self.member_id)
        is_subscribed = subscription_service.get_subscription_status_by_map_ids([node.map_id])[node.map_id]

        question_files_by_question_id = {}
        question_files = QuestionFile.objects.filter(
            question_id__in=question_ids,
        )
        for question_file in question_files:
            if question_file.question_id not in question_files_by_question_id:
                question_files_by_question_id[question_file.question_id] = []
            question_files_by_question_id[question_file.question_id].append(question_file)

        for arrow in arrows:
            if arrow.node_complete_rule_id not in question_dtos_by_rule_id:
                question_dtos_by_rule_id[arrow.node_complete_rule_id] = []

            question_status = 'locked'
            if arrow.question_id in members_completed_question_ids:
                question_status = 'completed'
            elif not node.is_active:
                question_status = 'deactivated'
            elif is_start_node:
                question_status = 'in_progress'
            elif arrow.start_node_id in members_completed_node_ids:
                question_status = 'in_progress'
            # Rule 안에 있에서 통해서 오는 것들이 전부다 해결이 됐어야 문제를 풀수 있도록 해야함
            elif arrow.start_node_id == arrow.end_node_id and node_status == 'in_progress':
                question_status = 'in_progress'

            answer_submittable = bool(
                self.member_id
                and self.map_play_member_id
                and question_status == 'in_progress'
                and is_subscribed
            )

            if arrow.question:
                question_dtos_by_rule_id[arrow.node_complete_rule_id].append(
                    # QuestionDTO 안에 문제를 해결할 수 있는 버튼 만들기 혹은 아니기 만들기 (비회원 및 나중을 위해)
                    QuestionDTO(
                        id=arrow.question.id,
                        arrow_id=arrow.id,
                        title=arrow.question.title,
                        description=arrow.question.description,
                        question_files=[
                            FileDTO(
                                id=file.id,
                                url=file.file,
                                name=file.name,
                            )
                            for file in question_files_by_question_id.get(arrow.question_id, [])
                        ],
                        status=question_status,
                        by_node_id=arrow.start_node_id,
                        answer_submit_with_text=QuestionType.TEXT.value in arrow.question.question_types,
                        answer_submit_with_file=QuestionType.FILE.value in arrow.question.question_types,
                        answer_submittable=answer_submittable,
                        my_answers=users_answers_by_question_id.get(arrow.question_id, []),
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
                        question_files=[],
                        status=(
                            'completed'
                            if (arrow.start_node_id in members_completed_node_ids)
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

    def _get_node_map_play_statistics(self, node: Node) -> Tuple[int, int]:
        completed_count = self._get_node_completed_in_map_play_count(node.id)
        activated_count = self._get_in_node_progress_in_map_play_count(node.id)

        return activated_count, completed_count

    def _get_node_completed_in_map_play_count(self, node_id: int) -> int:
        if not self.map_play_member:
            return 0

        return NodeCompletedHistory.objects.filter(
            node_id=node_id,
            map_play_member__map_play_id=self.map_play_member.map_play_id,
        ).count()

    def _get_before_node_solved_in_map_play_count(self, node_id: int) -> int:
        if not self.map_play_member:
            return 0
        start_node_ids = set(
            Arrow.objects.filter(
                node_complete_rule__node_id=node_id,
            ).values_list(
                'start_node_id',
                flat=True,
            )
        )
        return NodeCompletedHistory.objects.filter(
            node_id__in=start_node_ids,
            map_play_member__map_play_id=self.map_play_member.map_play_id,
        ).count()

    def _get_in_node_progress_in_map_play_count(self, node_id: int) -> int:
        return self._get_before_node_solved_in_map_play_count(node_id) - self._get_node_completed_in_map_play_count(node_id)
