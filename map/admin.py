from django.contrib import admin

from map.forms.admin_forms import MapAdminForm, NodeAdminForm, CategoryAdminForm
from map.models import (
    Arrow,
    ArrowProgress,
    Category,
    Map,
    MapCategory,
    Node,
    NodeCompleteRule,
    NodeCompletedHistory,
    PopularMap,
)


class MapCategoryInline(admin.TabularInline):
    model = MapCategory
    extra = 1
    autocomplete_fields = ['category']


@admin.register(Map)
class MapAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'subscriber_count', 'play_count', 'is_private', 'created_at')
    list_filter = ('is_private', 'is_deleted')
    search_fields = ('name', 'description')
    readonly_fields = ('subscriber_count', 'play_count', 'created_at', 'updated_at')
    form = MapAdminForm
    inlines = [MapCategoryInline]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('categories')


@admin.register(PopularMap)
class PopularMapAdmin(admin.ModelAdmin):
    list_display = ('map', 'type', 'created_at')
    list_filter = ('type', 'created_at')


@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'map', 'is_active', 'created_at')
    list_filter = ('is_active', 'is_deleted')
    search_fields = ('name', 'title', 'description', 'map__name')
    readonly_fields = ('created_at', 'updated_at')
    form = NodeAdminForm
    autocomplete_fields = ['map']


@admin.register(Arrow)
class ArrowAdmin(admin.ModelAdmin):
    list_display = (
        'map',
        'start_node',
        'node_complete_rule',
        'created_at',
    )
    list_filter = ('is_deleted',)
    search_fields = ('map__name', 'start_node__name', 'node_complete_rule__name')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ['map']

    class Media:
        js = ('map/js/admin_chained_selects.js',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj and obj.map_id:
            # 수정 시 map_id가 있는 경우 해당 map에 속한 start_node, node_complete_rule만 표시
            form.base_fields['start_node'].queryset = Node.objects.filter(map_id=obj.map_id, is_deleted=False)
            form.base_fields['node_complete_rule'].queryset = NodeCompleteRule.objects.filter(map_id=obj.map_id, is_deleted=False)
            # map_id가 있는 경우 해당 map에 속한 question만 표시
            from question.models import Question
            form.base_fields['question'].queryset = Question.objects.filter(map_id=obj.map_id, is_deleted=False)
        elif not obj:
            # 새로운 객체를 생성할 때는 초기에 모든 관련 객체를 숨김
            form.base_fields['start_node'].queryset = Node.objects.none()
            form.base_fields['node_complete_rule'].queryset = NodeCompleteRule.objects.none()
            from question.models import Question
            form.base_fields['question'].queryset = Question.objects.none()
        return form


@admin.register(NodeCompleteRule)
class NodeCompleteRuleAdmin(admin.ModelAdmin):
    list_display = ('node', 'map', 'created_at')
    list_filter = ('is_deleted',)
    search_fields = ('node__name', 'map__name', 'name')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ['map']

    class Media:
        js = ('map/js/admin_chained_selects.js',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj and obj.map_id:
            # 수정 시 map_id가 있는 경우 해당 map에 속한 node만 표시
            form.base_fields['node'].queryset = Node.objects.filter(map_id=obj.map_id, is_deleted=False)
        elif not obj:
            # 새로운 객체를 생성할 때는 초기에 모든 관련 객체를 숨김
            form.base_fields['node'].queryset = Node.objects.none()
        return form


@admin.register(NodeCompletedHistory)
class NodeCompletedHistoryAdmin(admin.ModelAdmin):
    list_display = ('node', 'member', 'completed_at')
    list_filter = ('completed_at',)
    search_fields = ('node__name', 'member__nickname', 'map__name')
    readonly_fields = ('completed_at', 'updated_at')


@admin.register(ArrowProgress)
class ArrowProgressAdmin(admin.ModelAdmin):
    list_display = (
        'arrow',
        'member',
        'map_play_member',
        'is_resolved',
        'resolved_at',
        'created_at',
    )
    list_filter = ('is_resolved',)
    search_fields = ('arrow__map__name', 'member__nickname')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    list_filter = ('is_deleted',)
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    form = CategoryAdminForm


@admin.register(MapCategory)
class MapCategoryAdmin(admin.ModelAdmin):
    list_display = ('map', 'category', 'created_at')
    list_filter = ('is_deleted',)
    search_fields = ('map__name', 'category__name')
    readonly_fields = ('created_at', 'updated_at')
