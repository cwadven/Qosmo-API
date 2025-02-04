from django.contrib import admin
from subscription.models import MapSubscription


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
