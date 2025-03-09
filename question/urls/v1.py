from django.urls import path

from question.views.answer_views import (
    AnswerSubmitView,
    UserQuestionAnswerDetailView,
)

app_name = 'question'

urlpatterns = [
    path('/<int:question_id>/answer/<int:map_play_member_id>/submit', AnswerSubmitView.as_view(), name='answer-submit'),
    path('/user-question-answer/<int:user_question_answer_id>', UserQuestionAnswerDetailView.as_view(), name='get-user-question-answer'),
]
