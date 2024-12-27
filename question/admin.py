from django.contrib import admin
from question.models import (
    Question,
    QuestionAnswer,
    UserQuestionAnswer,
    UserQuestionAnswerFile,
    QuestionFile,
)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'map',
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
