from django import forms

from question.models import UserQuestionAnswer


class FeedbackForm(forms.ModelForm):
    feedback = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        label='피드백 내용',
        help_text='학습자에게 전달할 피드백 내용을 작성해주세요.'
    )

    class Meta:
        model = UserQuestionAnswer
        fields = ['feedback', 'is_correct']
