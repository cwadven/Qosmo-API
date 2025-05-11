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
from play.models import MapPlayMember
from push.consts import PushChannelType
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

    def clean(self):
        """유효성 검사를 수행합니다"""
        cleaned_data = super().clean()
        
        # map이 변경되었는지 확인
        if 'map' in cleaned_data:
            map_obj = cleaned_data['map']
            arrow = cleaned_data.get('arrow')

            if arrow and arrow.map_id != map_obj.id:
                pass
        
        return cleaned_data


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
    autocomplete_fields = ['map']

    class Media:
        js = ('map/js/question_admin.js',)

    def get_question_types_display(self, obj):
        return ', '.join(obj.question_types)
    get_question_types_display.short_description = '문제 유형'
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # map_id 결정: 기존 객체 -> POST 데이터 -> GET 파라미터 순으로 확인
        map_id = None
        if obj and obj.map_id:
            map_id = obj.map_id
        elif request.method == 'POST' and 'map' in request.POST:
            map_id = request.POST.get('map')
        elif 'map' in request.GET:
            map_id = request.GET.get('map')
        
        if map_id:
            # 맵 ID가 있으면 관련 필드의 쿼리셋을 설정
            
            # 화살표 쿼리셋 설정
            from map.models import Arrow
            arrows_queryset = Arrow.objects.filter(map_id=map_id, is_deleted=False)
            form.base_fields['arrow'].queryset = arrows_queryset
        else:
            # 맵 ID가 없으면 빈 쿼리셋 설정
            from map.models import Arrow
            form.base_fields['arrow'].queryset = Arrow.objects.none()
        
        return form
        
    def save_model(self, request, obj, form, change):
        # 저장 로직은 수정하지 않고 그대로 진행
        super().save_model(request, obj, form, change)


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
    autocomplete_fields = ['map']
    
    class Media:
        js = ('map/js/question_answer_admin.js',)
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # 만약 객체가 이미 존재하거나 POST 요청에 question_id가 있다면
        question_id = None
        if obj and obj.question_id:
            question_id = obj.question_id
        elif request.method == 'POST' and 'question' in request.POST:
            question_id = request.POST.get('question')
        elif 'question' in request.GET:
            question_id = request.GET.get('question')
            
        # form에 데이터 초기값 설정 또는 추가 설정
        if question_id:
            # 필요한 경우 이 부분에 질문 ID에 따른 추가 로직 구현
            pass
            
        return form


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
                        if user_answer.question.arrow and user_answer.question.arrow.start_node:
                            node_completion_service = NodeCompletionService(
                                member_id=user_answer.member_id,
                                map_play_member_id=user_answer.map_play_member_id,
                                map_play_id=user_answer.map_play_member.map_play_id,
                            )
                            node_completion_service.process_nodes_completion(
                                nodes=[user_answer.question.arrow.start_node]
                            )
                    map_play_members = MapPlayMember.objects.filter(
                        map_play_id=user_answer.map_play_member.map_play.id,
                        deactivated=False,
                    )
                    try:
                        push_service = PushService()

                        answer_owner = Guest.objects.get(
                            member_id=user_answer.member_id,
                            member__is_active=True,
                        )
                        push_service.send_push(
                            guest_id=answer_owner.id,
                            title=f"\'{user_answer.question.title}\' 문제 결과",
                            body=feedback_obj.feedback,
                            push_channel_type=PushChannelType.QUESTION_FEEDBACK,
                            data={
                                "type": "question_feedback",
                                "question_id": str(user_answer.question.id),
                                "map_id": str(user_answer.question.arrow.map_id),
                                "map_play_member_id": str(user_answer.map_play_member_id),
                                "is_correct": str(feedback_obj.is_correct).lower(),
                            },
                        )

                        if feedback_obj.is_correct:
                            guests = Guest.objects.filter(
                                member_id__in=[map_play_member.member_id for map_play_member in map_play_members],
                                member__is_active=True,
                            ).exclude(
                                member_id=user_answer.member_id,
                            )
                            for guest in guests:
                                push_service.send_push(
                                    guest_id=guest.id,
                                    title=f"\'{user_answer.question.title}\' 문제 해결",
                                    body=f"{user_answer.member.nickname}님이 문제를 해결했습니다.",
                                    push_channel_type=PushChannelType.QUESTION_SOLVED_ALERT,
                                    data={
                                        "type": "question_solved_alert",
                                        "question_id": str(user_answer.question.id),
                                        "map_id": str(user_answer.question.arrow.map_id),
                                        "map_play_id": str(user_answer.map_play_member.map_play_id),
                                        "is_correct": True,
                                    },
                                )
                    except (Guest.DoesNotExist, Arrow.DoesNotExist):
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
    autocomplete_fields = ['map']
    
    class Media:
        js = ('map/js/question_file_admin.js',)
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # 만약 객체가 이미 존재하거나 POST 요청에 question_id가 있다면
        question_id = None
        if obj and obj.question_id:
            question_id = obj.question_id
        elif request.method == 'POST' and 'question' in request.POST:
            question_id = request.POST.get('question')
        elif 'question' in request.GET:
            question_id = request.GET.get('question')
            
        # form에 데이터 초기값 설정 또는 추가 설정
        if question_id:
            # 필요한 경우 이 부분에 질문 ID에 따른 추가 로직 구현
            pass
            
        return form
