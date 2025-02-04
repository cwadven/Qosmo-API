from django.contrib import admin
from subscription.models import MapSubscription, MapSubscriptionMember, MapSubscriptionBanned, \
    MapSubscriptionMemberRoleHistory, MapSubscriptionInviteCode


@admin.register(MapSubscription)
class MapSubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'member',
        'map',
        'is_deleted',
        'created_at',
        'updated_at',
    )
    list_filter = (
        'is_deleted',
        'created_at',
        'updated_at',
    )
    search_fields = (
        'member__nickname',
        'member__username',
        'map__name',
    )
    raw_id_fields = (
        'member',
        'map',
    )
    readonly_fields = (
        'created_at',
        'updated_at',
    )
    ordering = ('-created_at',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'member',
            'map',
        )


@admin.register(MapSubscriptionMember)
class MapSubscriptionMemberAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'map_subscription',
        'member',
        'role',
        'deactivated',
        'created_at',
        'updated_at',
    )
    readonly_fields = (
        'created_at',
        'updated_at',
    )


@admin.register(MapSubscriptionBanned)
class MapSubscriptionBannedAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'map_subscription',
        'member',
        'banned_by',
        'created_at',
        'updated_at',
    )
    readonly_fields = (
        'created_at',
        'updated_at',
    )


@admin.register(MapSubscriptionMemberRoleHistory)
class MapSubscriptionMemberRoleHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'map_subscription_member',
        'previous_role',
        'new_role',
        'created_at',
        'updated_at',
    )
    readonly_fields = (
        'created_at',
        'updated_at',
    )


@admin.register(MapSubscriptionInviteCode)
class MapSubscriptionInviteCodeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'map_subscription',
        'created_by',
        'max_uses',
        'expired_at',
        'is_active',
        'created_at',
        'updated_at',
    )
    readonly_fields = (
        'created_at',
        'updated_at',
    )
