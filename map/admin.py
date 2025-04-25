from django.contrib import admin
from django import forms

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


class ArrowAdminForm(forms.ModelForm):
    class Meta:
        model = Arrow
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 폼이 제출되면 맵 ID를 저장
        self.submitted_map_id = None
        self.submitted_start_node_id = None
        self.submitted_node_complete_rule_id = None
        self.submitted_question_id = None
        
        # 제출된 데이터가 있는 경우
        if 'data' in kwargs:
            data = kwargs['data']
            if 'map' in data:
                self.submitted_map_id = data.get('map')
            if 'start_node' in data:
                self.submitted_start_node_id = data.get('start_node')
            if 'node_complete_rule' in data:
                self.submitted_node_complete_rule_id = data.get('node_complete_rule')
            if 'question' in data:
                self.submitted_question_id = data.get('question')

    def save(self, commit=True):
        """
        데이터베이스 저장 메서드를 재정의하여 폼에서 누락된 필드를 직접 처리
        """
        # 기본 save 메서드 호출
        instance = super().save(commit=False)
        
        # 제출된 ID가 있지만 폼에서 처리되지 않은 경우 직접 처리
        try:
            # 맵 ID 설정 (필수 필드)
            if self.submitted_map_id and not instance.map_id:
                instance.map_id = self.submitted_map_id
                
            # 시작 노드 설정
            if self.submitted_start_node_id and not instance.start_node_id:
                instance.start_node_id = self.submitted_start_node_id
                
            # 노드 완료 규칙 설정
            if self.submitted_node_complete_rule_id and not instance.node_complete_rule_id:
                instance.node_complete_rule_id = self.submitted_node_complete_rule_id
                
            # 문제 설정
            if self.submitted_question_id and not instance.question_id:
                instance.question_id = self.submitted_question_id
        except Exception:
            pass
        
        # 변경사항 저장
        if commit:
            instance.save()
        
        return instance


class NodeCompleteRuleAdminForm(forms.ModelForm):
    class Meta:
        model = NodeCompleteRule
        fields = '__all__'
        
    def clean(self):
        """유효성 검사를 수행합니다"""
        cleaned_data = super().clean()
        
        # 로깅 추가
        print("===== NODE COMPLETE RULE FORM CLEAN =====")
        print(f"Cleaned data keys: {cleaned_data.keys()}")
        
        # map이 변경되었는지 확인
        if 'map' in cleaned_data:
            map_obj = cleaned_data['map']
            
            # node가 맵에 속하는지 확인
            node = cleaned_data.get('node')
            if node and node.map_id != map_obj.id:
                # 오류 메시지만 표시하고 값은 그대로 유지
                print(f"Node {node.id} does not belong to map {map_obj.id}")
                # self.add_error('node', '선택한 노드는 현재 맵에 속하지 않습니다. 다시 선택해주세요.')
        
        return cleaned_data


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

    class Media:
        js = ('map/js/node_admin.js',)


@admin.register(Arrow)
class ArrowAdmin(admin.ModelAdmin):
    form = ArrowAdminForm
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
        js = ('map/js/arrow_admin.js',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # map_id 결정: 기존 객체 -> POST 데이터 -> GET 파라미터 순으로 확인
        map_id = None
        if obj and obj.map_id:
            map_id = obj.map_id
        elif request.method == 'POST' and 'map' in request.POST:
            map_id = request.POST.get('map')
        elif 'map' in request.GET:
            map_id = request.GET.get('map')
        
        if map_id:
            # 맵 ID가 있으면 관련 필드의 쿼리셋을 설정
            # 노드 쿼리셋 설정
            nodes_queryset = Node.objects.filter(map_id=map_id, is_deleted=False)
            form.base_fields['start_node'].queryset = nodes_queryset
            
            # 노드 완료 규칙 쿼리셋 설정
            rules_queryset = NodeCompleteRule.objects.filter(map_id=map_id, is_deleted=False)
            form.base_fields['node_complete_rule'].queryset = rules_queryset
            
            # 문제 쿼리셋 설정
            from question.models import Question
            questions_queryset = Question.objects.filter(map_id=map_id, is_deleted=False)
            form.base_fields['question'].queryset = questions_queryset
        else:
            # 맵 ID가 없으면 빈 쿼리셋 설정
            form.base_fields['start_node'].queryset = Node.objects.none()
            form.base_fields['node_complete_rule'].queryset = NodeCompleteRule.objects.none()
            from question.models import Question
            form.base_fields['question'].queryset = Question.objects.none()
        
        return form
        
    def save_model(self, request, obj, form, change):
        # 저장 로직은 수정하지 않고 그대로 진행
        super().save_model(request, obj, form, change)


@admin.register(NodeCompleteRule)
class NodeCompleteRuleAdmin(admin.ModelAdmin):
    form = NodeCompleteRuleAdminForm
    list_display = ('node', 'map', 'created_at')
    list_filter = ('is_deleted',)
    search_fields = ('node__name', 'map__name', 'name')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ['map']

    class Media:
        js = ('map/js/node_complete_rule_admin.js',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # map_id 결정: 기존 객체 -> POST 데이터 -> GET 파라미터 순으로 확인
        map_id = None
        if obj and obj.map_id:
            map_id = obj.map_id
        elif request.method == 'POST' and 'map' in request.POST:
            map_id = request.POST.get('map')
        elif 'map' in request.GET:
            map_id = request.GET.get('map')
        
        if map_id:
            # 맵 ID가 있으면 관련 필드의 쿼리셋을 설정
            # 노드 쿼리셋 설정
            nodes_queryset = Node.objects.filter(map_id=map_id, is_deleted=False)
            form.base_fields['node'].queryset = nodes_queryset
            
            # 기존 객체가 있을 경우 현재 값들의 맵 ID 확인
            if obj and obj.node:
                print(f"Current node ID: {obj.node.id}, belongs to map: {obj.node.map_id}")
        else:
            # 맵 ID가 없으면 빈 쿼리셋 설정
            form.base_fields['node'].queryset = Node.objects.none()
        
        return form
        
    def save_model(self, request, obj, form, change):
        # 저장 로직은 수정하지 않고 그대로 진행
        super().save_model(request, obj, form, change)


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
