import boto3
from botocore.config import Config
from common.common_forms.admin_forms import PreSignedUrlAdminForm
from django import forms
from django.conf import settings

from question.models import QuestionFile


class QuestionFileAdminForm(PreSignedUrlAdminForm):
    file = forms.CharField(
        label='File',
        help_text='File',
        required=False,
    )
    question_file = forms.FileField(
        label='문제 참고 파일 업로드 하기',
        help_text='문제 참고 파일 업로드 하기.',
        required=False,
    )

    class Meta:
        model = QuestionFile
        fields = '__all__'
        target_field_by_file_or_image_field = {
            'question_file': 'file',
        }
        upload_image_type = 'question_file'
        boto_client = boto3.client(
            's3',
            region_name='ap-northeast-2',
            aws_access_key_id=settings.AWS_IAM_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_IAM_SECRET_ACCESS_KEY,
            config=Config(signature_version='s3v4')
        )
        upload_bucket_name = settings.AWS_S3_BUCKET_NAME
