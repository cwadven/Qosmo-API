from django.contrib.postgres.fields import ArrayField
from django.db import models
from map.models import Map
from member.models import Member
from question.consts import (
    QuestionType,
    ValidationType,
)


class Question(models.Model):
    map = models.ForeignKey(
        Map,
        on_delete=models.DO_NOTHING,
        related_name='questions'
    )
    title = models.CharField(max_length=255)
    question_types = ArrayField(
        models.CharField(max_length=20, choices=QuestionType.choices()),
    )
    description = models.TextField()
    answer_validation_type = models.CharField(
        max_length=20,
        choices=ValidationType.choices(),
        help_text='정답 검증 방식'
    )
    is_by_pass = models.BooleanField(default=False, help_text='정답 검증을 하지 않음')
    default_success_feedback = models.TextField(blank=True, null=True, help_text='정답 시 표시할 피드백 메시지')
    default_failure_feedback = models.TextField(blank=True, null=True, help_text='오답 시 표시할 피드백 메시지')
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '문제'
        verbose_name_plural = '문제'

    def __str__(self):
        return self.title


class QuestionAnswer(models.Model):
    map = models.ForeignKey(
        Map,
        on_delete=models.DO_NOTHING,
        related_name='question_answers'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.DO_NOTHING,
        related_name='answers'
    )
    answer = models.TextField(help_text='정답')
    description = models.TextField(help_text='정답에 대한 설명')
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '문제 정답'
        verbose_name_plural = '문제 정답'

    def __str__(self):
        return f'{self.question.title}의 정답'


class UserQuestionAnswer(models.Model):
    map = models.ForeignKey(
        Map,
        on_delete=models.DO_NOTHING,
        related_name='user_answers',
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.DO_NOTHING,
        related_name='user_answers',
    )
    member = models.ForeignKey(
        Member,
        on_delete=models.DO_NOTHING,
        related_name='question_answers',
    )
    map_play_member = models.ForeignKey(
        'play.MapPlayMember',
        on_delete=models.DO_NOTHING,
        related_name='user_answers',
        null=True,
        blank=True,
    )
    answer = models.TextField()
    is_correct = models.BooleanField(
        null=True,
        blank=True,
    )
    feedback = models.TextField(
        null=True,
        blank=True,
        help_text='관리자의 피드백 내용',
    )
    reviewed_by = models.ForeignKey(
        Member,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name='reviewed_answers',
        help_text='검토한 관리자',
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='검토 시각',
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '사용자 답변'
        verbose_name_plural = '사용자 답변'

    def __str__(self):
        return f'{self.member.nickname}의 {self.question.title} 답변'


class UserQuestionAnswerFile(models.Model):
    map = models.ForeignKey(
        Map,
        on_delete=models.DO_NOTHING,
        related_name='user_answer_files'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.DO_NOTHING,
        related_name='user_answer_files'
    )
    user_question_answer = models.ForeignKey(
        UserQuestionAnswer,
        on_delete=models.DO_NOTHING,
        related_name='files'
    )
    name = models.CharField(
        max_length=255,
        help_text='파일 이름',
        null=True,
        blank=True,
    )
    file = models.CharField(
        max_length=255,
        help_text='S3 file path'
    )
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '사용자 답변 파일'
        verbose_name_plural = '사용자 답변 파일'

    def __str__(self):
        return f'{self.user_question_answer}의 파일'


class QuestionFile(models.Model):
    map = models.ForeignKey(
        Map,
        on_delete=models.DO_NOTHING,
        related_name='question_files'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.DO_NOTHING,
        related_name='files'
    )
    name = models.CharField(
        max_length=255,
        help_text='파일 이름',
        null=True,
        blank=True,
    )
    file = models.CharField(
        max_length=255,
        help_text='S3 file path'
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '문제 파일'
        verbose_name_plural = '문제 파일'

    def __str__(self):
        return f'{self.question.title}의 파일'
