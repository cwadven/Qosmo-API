from common.views import (
    ConstanceTypeView,
    GetFilePreSignedURLView,
    GetImagePreSignedURLView,
    HealthCheckView,
    UploadFilePreSignedURLView,
)
from django.urls import path

app_name = 'common'


urlpatterns = [
    path('/health_check', HealthCheckView.as_view(), name='health_check'),
    path('/<str:constance_type>/type', ConstanceTypeView.as_view(), name='constance_type'),

    path('/image/<str:constance_type>/<str:transaction_pk>/url', GetImagePreSignedURLView.as_view(), name='get_pre_signed_url'),
    path('/file/<str:constance_type>/<str:transaction_pk>/url', GetFilePreSignedURLView.as_view(), name='get_file_pre_signed_url'),
    path('/file/upload', UploadFilePreSignedURLView.as_view(), name='upload_file'),
]
