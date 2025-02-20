from django.contrib import admin
from django.contrib import messages
from django.forms import (
    CheckboxSelectMultiple,
    ModelForm,
    MultipleChoiceField,
)
from django.urls import reverse
from django.utils.html import format_html
from django.template.response import TemplateResponse
from django.utils import timezone

from map.models import Arrow
from member.models import Guest
from question.consts import QuestionType
from question.forms.admin_forms import QuestionFileAdminForm
from question.forms.client_forms import FeedbackForm
from question.models import (
    Question,
    QuestionAnswer,
    QuestionFile,
    UserQuestionAnswer,
    UserQuestionAnswerFile,
)
from django.http import HttpResponseRedirect
from question.services.node_completion_service import NodeCompletionService
from django.db import transaction
from push.services import PushService


class QuestionAdminForm(ModelForm):
    question_types = MultipleChoiceField(
        choices=QuestionType.choices(),
        widget=CheckboxSelectMultiple,
        help_text='문제 유형 (복수 선택 가능)',
    )

    class Meta:
        model = Question
        fields = '__all__'

    def clean_question_types(self):
        return list(self.cleaned_data['question_types'])


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    form = QuestionAdminForm
    list_display = (
        'title',
        'map',
        'get_question_types_display',
        'answer_validation_type',
        'is_by_pass',
        'created_at',
    )
    list_filter = (
        'answer_validation_type',
        'is_by_pass',
        'is_deleted',
    )
    search_fields = ('title', 'description', 'map__name')
    readonly_fields = ('created_at', 'updated_at')

    def get_question_types_display(self, obj):
        return ', '.join(obj.question_types)
    get_question_types_display.short_description = '문제 유형'


@admin.register(QuestionAnswer)
class QuestionAnswerAdmin(admin.ModelAdmin):
    list_display = (
        'question',
        'answer',
        'created_at',
    )
    list_filter = ('is_deleted',)
    search_fields = (
        'question__title',
        'answer',
        'description',
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(UserQuestionAnswer)
class UserQuestionAnswerAdmin(admin.ModelAdmin):
    list_display = (
        'question',
        'member',
        'is_correct',
        'reviewed_by',
        'reviewed_at',
        'created_at',
    )
    list_filter = (
        'is_correct',
        'reviewed_at',
    )
    search_fields = (
        'question__title',
        'member__nickname',
        'answer',
    )
    readonly_fields = ('created_at', 'updated_at', 'feedback_button')

    def feedback_button(self, obj):
        if obj.pk:  # 객체가 저장되어 있을 때만 버튼 표시
            url = reverse('admin:question_userquestionanswer_feedback', args=[obj.pk])
            return format_html(
                '<a class="button" href="{}">문제 피드백하기</a>',
                url
            )
        return ""
    feedback_button.short_description = ""  # 필드 라벨 제거

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/feedback/',
                self.admin_site.admin_view(self.feedback_view),
                name='question_userquestionanswer_feedback'
            ),
        ]
        return custom_urls + urls

    def feedback_view(self, request, object_id):
        user_answer = self.get_object(request, object_id)
        if not user_answer:
            messages.error(request, '해당 답변을 찾을 수 없습니다.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

        # 연관된 파일들 조회
        answer_files = UserQuestionAnswerFile.objects.filter(
            user_question_answer=user_answer,
            is_deleted=False,
        )

        if request.method == 'POST':
            form = FeedbackForm(request.POST, instance=user_answer)
            if form.is_valid():
                with transaction.atomic():
                    feedback_obj = form.save(commit=False)
                    feedback_obj.reviewed_by = request.user
                    feedback_obj.reviewed_at = timezone.now()
                    feedback_obj.save()

                    # 정답인 경우 노드 완료 처리
                    if feedback_obj.is_correct:
                        # Question과 연결된 Arrow의 start_node 찾기
                        # 지금은 무조건 1개의 arrow 는 1개의 question 가정
                        arrow = Arrow.objects.filter(
                            question=user_answer.question,
                            is_deleted=False
                        ).first()

                        if arrow and arrow.start_node:
                            node_completion_service = NodeCompletionService(
                                member_id=user_answer.member_id,
                                map_play_member_id=user_answer.map_play_member_id,
                            )
                            node_completion_service.process_nodes_completion(
                                nodes=[arrow.start_node]
                            )

                    try:
                        guest = Guest.objects.get(member_id=user_answer.member_id, member__is_active=True)
                        push_service = PushService()
                        push_service.send_push(
                            guest_id=guest.id,
                            title=f"\'{user_answer.question.title}\' 문제 결과",
                            body=feedback_obj.feedback,
                            data={
                                "type": "question_feedback",
                                "question_id": str(user_answer.question.id),
                                "is_correct": str(feedback_obj.is_correct).lower(),
                            },
                        )
                    except Guest.DoesNotExist:
                        pass

                messages.success(request, '피드백이 성공적으로 저장되었습니다.')
                return HttpResponseRedirect(
                    reverse('admin:question_userquestionanswer_change', args=[object_id])
                )
        else:
            form = FeedbackForm(instance=user_answer)

        context = {
            **self.admin_site.each_context(request),
            'opts': self.model._meta,
            'form': form,
            'original': user_answer,
            'answer_files': answer_files,  # 파일 목록 추가
            'title': '문제 피드백',
        }

        return TemplateResponse(
            request,
            'admin/question/userquestionanswer/feedback.html',
            context,
        )


@admin.register(UserQuestionAnswerFile)
class UserQuestionAnswerFileAdmin(admin.ModelAdmin):
    list_display = (
        'user_question_answer',
        'file',
        'created_at',
    )
    list_filter = ('is_deleted',)
    search_fields = (
        'user_question_answer__question__title',
        'user_question_answer__member__nickname',
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(QuestionFile)
class QuestionFileAdmin(admin.ModelAdmin):
    list_display = (
        'question',
        'name',
        'file',
        'created_at',
    )
    search_fields = ('question__title',)
    readonly_fields = ('created_at', 'updated_at')
    form = QuestionFileAdminForm
