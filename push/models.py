from django.db import models


class UserQuestionAnswerPushToken(models.Model):
    user_question_answer = models.ForeignKey('question.UserQuestionAnswer', on_delete=models.DO_NOTHING)
    device_token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
