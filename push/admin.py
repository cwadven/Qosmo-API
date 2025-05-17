from django.contrib import admin
from push.models import (
    DeviceToken,
    PushHistory,
    PushMapPlayMember,
)


@admin.register(DeviceToken)
class DeviceTokenAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'guest',
        'token',
        'device_type',
        'is_active',
        'created_at',
        'updated_at',
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(PushHistory)
class PushHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'guest',
        'device_token',
        'title',
        'body',
        'data',
        'sent_at',
        'is_success',
        'error_message',
    )
    readonly_fields = ('sent_at',)


@admin.register(PushMapPlayMember)
class PushHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'map_play_member',
        'guest',
        'push_type',
        'is_active',
    )
