from django.apps import AppConfig
import firebase_admin
from firebase_admin import credentials
from django.conf import settings


class PushConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'push'

    def ready(self):
        """
        앱이 시작될 때 Firebase Admin SDK 초기화
        """
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
                firebase_admin.initialize_app(cred)
        except Exception as e:
            print(f"Firebase Admin SDK 초기화 실패: {e}")
