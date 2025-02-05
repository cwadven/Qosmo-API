from django.contrib import admin

from play.models import (
    MapPlay,
    MapPlayMember,
    MapPlayBanned,
    MapPlayMemberRoleHistory,
    MapPlayInviteCode,
)


@admin.register(MapPlay)
class MapPlayAdmin(admin.ModelAdmin):
    list_display = ('id', 'map', 'title', 'created_by', 'created_at')
    search_fields = ('title', 'map__name', 'created_by__nickname')
    readonly_fields = ('created_at', 'updated_at')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('map', 'created_by')


@admin.register(MapPlayMember)
class MapPlayMemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'map_play', 'get_map_name', 'member', 'role', 'deactivated', 'created_at')
    search_fields = ('map_play__title', 'map_play__map__name', 'member__nickname')
    readonly_fields = ('created_at', 'updated_at')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'map_play',
            'map_play__map',
            'member'
        )

    def get_map_name(self, obj):
        return obj.map_play.map.name
    get_map_name.short_description = '맵'
    get_map_name.admin_order_field = 'map_play__map__name'


@admin.register(MapPlayBanned)
class MapPlayBannedAdmin(admin.ModelAdmin):
    list_display = ('id', 'map_play', 'get_map_name', 'member', 'banned_by', 'banned_at')
    search_fields = ('map_play__title', 'map_play__map__name', 'member__nickname', 'banned_by__nickname')
    readonly_fields = ('banned_at', 'created_at', 'updated_at')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'map_play',
            'map_play__map',
            'member',
            'banned_by'
        )

    def get_map_name(self, obj):
        return obj.map_play.map.name
    get_map_name.short_description = '맵'
    get_map_name.admin_order_field = 'map_play__map__name'


@admin.register(MapPlayMemberRoleHistory)
class MapPlayMemberRoleHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'map_play_member', 'get_map_name', 'previous_role', 'new_role', 'changed_by', 'created_at')
    search_fields = ('map_play_member__map_play__title', 'map_play_member__map_play__map__name', 'map_play_member__member__nickname', 'changed_by__nickname')
    readonly_fields = ('created_at', 'updated_at')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'map_play_member',
            'map_play_member__map_play',
            'map_play_member__map_play__map',
            'map_play_member__member',
            'changed_by'
        )

    def get_map_name(self, obj):
        return obj.map_play_member.map_play.map.name
    get_map_name.short_description = '맵'
    get_map_name.admin_order_field = 'map_play_member__map_play__map__name'


@admin.register(MapPlayInviteCode)
class MapPlayInviteCodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'map_play', 'get_map_name', 'code', 'created_by', 'max_uses', 'current_uses', 'expired_at', 'is_active')
    search_fields = ('code', 'map_play__title', 'map_play__map__name', 'created_by__nickname')
    readonly_fields = ('created_at', 'updated_at')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'map_play',
            'map_play__map',
            'created_by'
        )

    def get_map_name(self, obj):
        return obj.map_play.map.name
    get_map_name.short_description = '맵'
    get_map_name.admin_order_field = 'map_play__map__name'
