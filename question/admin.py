from django.contrib import admin
from django.forms import ModelForm, MultipleChoiceField, CheckboxSelectMultiple
from question.models import (
    Question,
    QuestionAnswer,
    UserQuestionAnswer,
    UserQuestionAnswerFile,
    QuestionFile,
)
from question.consts import QuestionType


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
    readonly_fields = ('created_at', 'updated_at')


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
        'file',
        'created_at',
    )
    search_fields = ('question__title',)
    readonly_fields = ('created_at', 'updated_at')
