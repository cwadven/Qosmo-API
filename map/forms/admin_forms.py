import boto3
from botocore.config import Config
from common.common_forms.admin_forms import PreSignedUrlAdminForm
from django import forms
from django.conf import settings

from map.models import (
    Category,
    Map,
    Node,
)


class MapAdminForm(PreSignedUrlAdminForm):
    icon_image = forms.CharField(
        required=False,
    )
    background_image = forms.CharField(
        required=False,
    )
    icon_image_file = forms.ImageField(
        label='아이콘 이미지 업로드 하기',
        help_text='이미지를 업로드 후, 저장하면 URL이 자동으로 입력됩니다.',
        required=False,
    )
    background_image_file = forms.ImageField(
        label='백그라운 이미지 업로드 하기',
        help_text='이미지를 업로드 후, 저장하면 URL이 자동으로 입력됩니다.',
        required=False,
    )

    class Meta:
        model = Map
        fields = '__all__'
        target_field_by_file_or_image_field = {
            'icon_image_file': 'icon_image',
            'background_image_file': 'background_image',
        }
        upload_image_type = 'map_image'
        boto_client = boto3.client(
            's3',
            region_name='ap-northeast-2',
            aws_access_key_id=settings.AWS_IAM_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_IAM_SECRET_ACCESS_KEY,
            config=Config(signature_version='s3v4')
        )
        upload_bucket_name = settings.AWS_S3_BUCKET_NAME


class NodeAdminForm(PreSignedUrlAdminForm):
    background_image_file = forms.ImageField(
        label='백그라운 이미지 업로드 하기',
        help_text='이미지를 업로드 후, 저장하면 URL이 자동으로 입력됩니다.',
        required=False,
    )

    class Meta:
        model = Node
        fields = '__all__'
        target_field_by_file_or_image_field = {
            'background_image_file': 'background_image',
        }
        upload_image_type = 'node_image'
        boto_client = boto3.client(
            's3',
            region_name='ap-northeast-2',
            aws_access_key_id=settings.AWS_IAM_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_IAM_SECRET_ACCESS_KEY,
            config=Config(signature_version='s3v4')
        )
        upload_bucket_name = settings.AWS_S3_BUCKET_NAME


class CategoryAdminForm(PreSignedUrlAdminForm):
    icon_image_file = forms.ImageField(
        label='아이콘 이미지 업로드 하기',
        help_text='이미지를 업로드 후, 저장하면 URL이 자동으로 입력됩니다.',
        required=False,
    )

    class Meta:
        model = Category
        fields = '__all__'
        target_field_by_file_or_image_field = {
            'icon_image_file': 'icon',
        }
        upload_image_type = 'node_image'
        boto_client = boto3.client(
            's3',
            region_name='ap-northeast-2',
            aws_access_key_id=settings.AWS_IAM_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_IAM_SECRET_ACCESS_KEY,
            config=Config(signature_version='s3v4')
        )
        upload_bucket_name = settings.AWS_S3_BUCKET_NAME
