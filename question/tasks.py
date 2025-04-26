from typing import (
    Dict,
    List,
)

from common.common_utils import send_email
from config.celery import app


# send_question_submitted_email.apply_async(...)
@app.task
def send_question_submitted_email(
        emails: List[str],
        nickname: str,
        map_name: str,
        question_title: str,
        user_answer: str,
        files: List[Dict[str, str]],
        user_answer_id: int,
) -> None:
    """
    file_links: [{'name': 'file_name', 'url': 'file_url'}, ...]
    """
    send_email(
        f'사용자가 \'{map_name}\' 에 문제 결과를 제출했습니다.',
        'email/question/question_submitted.html',
        {
            'nickname': nickname,
            'question_title': question_title,
            'user_answer': user_answer,
            'files': files,
            'deeplink': '',
        },
        emails
    )
