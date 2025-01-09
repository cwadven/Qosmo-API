from django.urls import path
from question.views.answer_views import AnswerSubmitView

app_name = 'question'

urlpatterns = [
    path('<int:question_id>/answer/submit', AnswerSubmitView.as_view(), name='answer-submit'),
]
