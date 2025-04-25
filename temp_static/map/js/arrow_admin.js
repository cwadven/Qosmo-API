// Arrow 모델 관리자 페이지용 스크립트
window.addEventListener('load', function() {
    // 가능한 모든 jQuery 참조 시도
    var jq = window.jQuery || window.django && window.django.jQuery || (typeof django !== 'undefined' && django.jQuery);
    
    if (jq) {
        console.log('jQuery를 찾았습니다!');
        initArrowAdmin(jq);
    } else {
        // 1초마다 jQuery를 찾아보기
        console.log('Django 관리자 페이지의 jQuery를 기다립니다...');
        var attempts = 0;
        var checkInterval = setInterval(function() {
            attempts++;
            jq = window.jQuery || window.django && window.django.jQuery || (typeof django !== 'undefined' && django.jQuery);
            
            if (jq) {
                console.log('jQuery를 찾았습니다! (시도 횟수: ' + attempts + ')');
                clearInterval(checkInterval);
                initArrowAdmin(jq);
            }
            
            if (attempts >= 10) {
                console.error('10번 시도 후에도 jQuery를 찾지 못했습니다.');
                clearInterval(checkInterval);
            }
        }, 500);
    }
});

function initArrowAdmin($) {
    console.log('Arrow admin 스크립트 초기화');
    
    if ($('#id_map').length > 0 && $('#id_start_node').length > 0 && $('#id_end_node').length > 0) {
        console.log('Arrow admin form 감지됨');
        
        // 처음 페이지 로딩 시 초기 상태 저장
        var initialStartNodeHtml = $('#id_start_node').html() || '';
        var initialEndNodeHtml = $('#id_end_node').html() || '';
        
        console.log('Map ID 현재 값:', $('#id_map').val());
        
        // 맵이 이미 선택되어 있다면 관련 필드 업데이트 트리거
        var currentMapId = $('#id_map').val();
        if (currentMapId) {
            console.log('이미 선택된 Map ID가 있어 관련 필드를 업데이트합니다:', currentMapId);
            // AJAX 요청 - Node 필터링
            $.ajax({
                url: '/v1/map-admin/get-nodes-by-map',
                data: {
                    'map_id': currentMapId
                },
                dataType: 'json',
                success: function(data) {
                    console.log('노드 로드됨:', data.length);
                    var options = '<option value="">---------</option>';
                    $.each(data, function(index, item) {
                        options += '<option value="' + item.id + '">' + item.name + '</option>';
                    });
                    $('#id_start_node').html(options);
                    $('#id_end_node').html(options);
                    
                    // 이미 선택된 값이 있다면 유지
                    var preSelectedStartValue = $('#id_start_node').attr('data-initial-value');
                    var preSelectedEndValue = $('#id_end_node').attr('data-initial-value');
                    
                    if (preSelectedStartValue) {
                        $('#id_start_node').val(preSelectedStartValue);
                    }
                    
                    if (preSelectedEndValue) {
                        $('#id_end_node').val(preSelectedEndValue);
                    }
                },
                error: function(xhr, status, error) {
                    console.error('노드 데이터를 가져오는 중 오류 발생:', error);
                    console.error('상태 코드:', xhr.status);
                    console.error('응답 텍스트:', xhr.responseText);
                }
            });
        }
        
        // 맵 변경 시 이벤트 핸들러
        $('#id_map').on('change', function() {
            var mapId = $(this).val();
            console.log('Map 변경됨:', mapId);
            
            // 맵이 선택되지 않았으면 초기 상태로 돌림
            if (!mapId) {
                $('#id_start_node').html(initialStartNodeHtml);
                $('#id_end_node').html(initialEndNodeHtml);
                return;
            }
            
            // AJAX 요청 - Node 필터링
            $.ajax({
                url: '/v1/map-admin/get-nodes-by-map',
                data: {
                    'map_id': mapId
                },
                dataType: 'json',
                success: function(data) {
                    console.log('노드 로드됨:', data.length);
                    var options = '<option value="">---------</option>';
                    $.each(data, function(index, item) {
                        options += '<option value="' + item.id + '">' + item.name + '</option>';
                    });
                    $('#id_start_node').html(options);
                    $('#id_end_node').html(options);
                },
                error: function(xhr, status, error) {
                    console.error('노드 데이터를 가져오는 중 오류 발생:', error);
                    console.error('상태 코드:', xhr.status);
                    console.error('응답 텍스트:', xhr.responseText);
                }
            });
        });
    }
} 