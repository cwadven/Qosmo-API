// Django 관리자 페이지를 위한 chained select fields - 더 단순한 접근 방식
window.addEventListener('load', function() {
    // 가능한 모든 jQuery 참조 시도
    var jq = window.jQuery || window.django && window.django.jQuery || (typeof django !== 'undefined' && django.jQuery);
    
    if (jq) {
        console.log('jQuery를 찾았습니다!');
        initChainedSelects(jq);
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
                initChainedSelects(jq);
            }
            
            if (attempts >= 10) {
                console.error('10번 시도 후에도 jQuery를 찾지 못했습니다.');
                clearInterval(checkInterval);
            }
        }, 500);
    }
    
    // 초기화 함수
    function initChainedSelects($) {
        console.log('Django admin chained selects 초기화 중...');
        
        // URL 테스트
        testApiEndpoints($);
        
        // Question 모델 관련 스크립트
        if ($('#id_map').length > 0 && $('#id_arrow').length > 0 && $('#id_start_node').length === 0 && $('#id_node').length === 0) {
            console.log('Question admin form 감지됨');
            
            // 처음 페이지 로딩 시 초기 상태 저장
            var initialArrowHtml = $('#id_arrow').html() || '';
            
            console.log('Map ID 현재 값:', $('#id_map').val());
            
            // 맵이 이미 선택되어 있다면 관련 필드 업데이트 트리거
            var currentMapId = $('#id_map').val();
            if (currentMapId) {
                console.log('이미 선택된 Map ID가 있어 Arrow 필드를 업데이트합니다:', currentMapId);
                // AJAX 요청 - Arrow 필터링
                $.ajax({
                    url: '/v1/map-admin/get-arrows-by-map',
                    data: {
                        'map_id': currentMapId,
                        'same_node': 'true',
                    },
                    dataType: 'json',
                    success: function(data) {
                        console.log('화살표 로드됨:', data.length);
                        var options = '<option value="">---------</option>';
                        $.each(data, function(index, item) {
                            options += '<option value="' + item.id + '">' + item.name + '</option>';
                        });
                        $('#id_arrow').html(options);
                        
                        // 이미 선택된 값이 있다면 유지
                        var preSelectedValue = $('#id_arrow').attr('data-initial-value');
                        if (preSelectedValue) {
                            $('#id_arrow').val(preSelectedValue);
                        }
                    },
                    error: function(xhr, status, error) {
                        console.error('화살표 데이터를 가져오는 중 오류 발생:', error);
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
                    $('#id_arrow').html(initialArrowHtml);
                    return;
                }
                // AJAX 요청 - Arrow 필터링
                $.ajax({
                    url: '/v1/map-admin/get-arrows-by-map',
                    data: {
                        'map_id': mapId,
                        'same_node': 'true',
                    },
                    dataType: 'json',
                    success: function(data) {
                        console.log('화살표 로드됨:', data.length);
                        var options = '<option value="">---------</option>';
                        $.each(data, function(index, item) {
                            options += '<option value="' + item.id + '">' + item.name + '</option>';
                        });
                        $('#id_arrow').html(options);
                    },
                    error: function(xhr, status, error) {
                        console.error('화살표 데이터를 가져오는 중 오류 발생:', error);
                        console.error('상태 코드:', xhr.status);
                        console.error('응답 텍스트:', xhr.responseText);
                    }
                });
            });
        }
        
        // Arrow 모델 관련 스크립트
        if ($('#id_map').length > 0 && ($('#id_start_node').length > 0 || $('#id_node_complete_rule').length > 0 || $('#id_question').length > 0)) {
            console.log('Arrow admin form 감지됨');
            
            // 처음 페이지 로딩 시 초기 상태 저장
            var initialStartNodeHtml = $('#id_start_node').html() || '';
            var initialNodeCompleteRuleHtml = $('#id_node_complete_rule').html() || '';
            var initialQuestionHtml = $('#id_question').html() || '';
            
            console.log('Map ID 현재 값:', $('#id_map').val());
            
            // 맵이 이미 선택되어 있다면 관련 필드 업데이트 트리거
            var currentMapId = $('#id_map').val();
            if (currentMapId) {
                console.log('이미 선택된 Map ID가 있어 관련 필드를 업데이트합니다:', currentMapId);
                updateRelatedFields($, currentMapId);
            }
            
            // 맵 변경 시 이벤트 핸들러
            $('#id_map').on('change', function() {
                var mapId = $(this).val();
                console.log('Map 변경됨:', mapId);
                
                // 맵이 선택되지 않았으면 초기 상태로 돌림
                if (!mapId) {
                    if ($('#id_start_node').length > 0) {
                        $('#id_start_node').html(initialStartNodeHtml);
                    }
                    if ($('#id_node_complete_rule').length > 0) {
                        $('#id_node_complete_rule').html(initialNodeCompleteRuleHtml);
                    }
                    if ($('#id_question').length > 0) {
                        $('#id_question').html(initialQuestionHtml);
                    }
                    return;
                }
                
                updateRelatedFields($, mapId);
            });
        }
        
        // NodeCompleteRule 모델 관련 스크립트
        if ($('#id_map').length > 0 && $('#id_node').length > 0 && $('#id_start_node').length === 0) {
            console.log('NodeCompleteRule admin form 감지됨');
            
            // 처음 페이지 로딩 시 초기 상태 저장
            var initialNodeHtml = $('#id_node').html() || '';
            
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
                        $('#id_node').html(options);
                        
                        // 이미 선택된 값이 있다면 유지
                        var preSelectedValue = $('#id_node').attr('data-initial-value');
                        if (preSelectedValue) {
                            $('#id_node').val(preSelectedValue);
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
                    $('#id_node').html(initialNodeHtml);
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
                        $('#id_node').html(options);
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
    
    function updateRelatedFields($, mapId) {
        // AJAX 요청 - Start Node 필터링
        if ($('#id_start_node').length > 0) {
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
                    
                    // 이미 선택된 값이 있다면 유지
                    var preSelectedValue = $('#id_start_node').attr('data-initial-value');
                    if (preSelectedValue) {
                        $('#id_start_node').val(preSelectedValue);
                    }
                },
                error: function(xhr, status, error) {
                    console.error('노드 데이터를 가져오는 중 오류 발생:', error);
                    console.error('상태 코드:', xhr.status);
                    console.error('응답 텍스트:', xhr.responseText);
                }
            });
        }
        
        // AJAX 요청 - Node Complete Rule 필터링
        if ($('#id_node_complete_rule').length > 0) {
            $.ajax({
                url: '/v1/map-admin/get-node-complete-rules-by-map',
                data: {
                    'map_id': mapId
                },
                dataType: 'json',
                success: function(data) {
                    console.log('노드 완료 규칙 로드됨:', data.length);
                    var options = '<option value="">---------</option>';
                    $.each(data, function(index, item) {
                        options += '<option value="' + item.id + '">' + item.name + '</option>';
                    });
                    $('#id_node_complete_rule').html(options);
                    
                    // 이미 선택된 값이 있다면 유지
                    var preSelectedValue = $('#id_node_complete_rule').attr('data-initial-value');
                    if (preSelectedValue) {
                        $('#id_node_complete_rule').val(preSelectedValue);
                    }
                },
                error: function(xhr, status, error) {
                    console.error('노드 완료 규칙 데이터를 가져오는 중 오류 발생:', error);
                    console.error('상태 코드:', xhr.status);
                    console.error('응답 텍스트:', xhr.responseText);
                }
            });
        }
        
        // AJAX 요청 - Question 필터링
        if ($('#id_question').length > 0) {
            $.ajax({
                url: '/v1/map-admin/get-questions-by-map',
                data: {
                    'map_id': mapId
                },
                dataType: 'json',
                success: function(data) {
                    console.log('문제 로드됨:', data.length);
                    var options = '<option value="">---------</option>';
                    $.each(data, function(index, item) {
                        options += '<option value="' + item.id + '">' + item.title + '</option>';
                    });
                    $('#id_question').html(options);
                    
                    // 이미 선택된 값이 있다면 유지
                    var preSelectedValue = $('#id_question').attr('data-initial-value');
                    if (preSelectedValue) {
                        $('#id_question').val(preSelectedValue);
                    }
                },
                error: function(xhr, status, error) {
                    console.error('문제 데이터를 가져오는 중 오류 발생:', error);
                    console.error('상태 코드:', xhr.status);
                    console.error('응답 텍스트:', xhr.responseText);
                }
            });
        }
    }
    
    function testApiEndpoints($) {
        // API 엔드포인트 테스트
        console.log('API 엔드포인트 테스트 시작...');
        
        // 임의의 map_id로 테스트
        var testMapId = 1;
        
        $.ajax({
            url: '/v1/map-admin/get-nodes-by-map',
            data: {
                'map_id': testMapId
            },
            dataType: 'json',
            success: function(data) {
                console.log('API 테스트 성공 - get-nodes-by-map:', data);
            },
            error: function(xhr, status, error) {
                console.error('API 테스트 실패 - get-nodes-by-map');
                console.error('상태 코드:', xhr.status);
                console.error('응답 텍스트:', xhr.responseText);
            }
        });
        
        $.ajax({
            url: '/v1/map-admin/get-node-complete-rules-by-map',
            data: {
                'map_id': testMapId
            },
            dataType: 'json',
            success: function(data) {
                console.log('API 테스트 성공 - get-node-complete-rules-by-map:', data);
            },
            error: function(xhr, status, error) {
                console.error('API 테스트 실패 - get-node-complete-rules-by-map');
                console.error('상태 코드:', xhr.status);
                console.error('응답 텍스트:', xhr.responseText);
            }
        });
        
        $.ajax({
            url: '/v1/map-admin/get-questions-by-map',
            data: {
                'map_id': testMapId
            },
            dataType: 'json',
            success: function(data) {
                console.log('API 테스트 성공 - get-questions-by-map:', data);
            },
            error: function(xhr, status, error) {
                console.error('API 테스트 실패 - get-questions-by-map');
                console.error('상태 코드:', xhr.status);
                console.error('응답 텍스트:', xhr.responseText);
            }
        });
        
        $.ajax({
            url: '/v1/map-admin/get-arrows-by-map',
            data: {
                'map_id': testMapId
            },
            dataType: 'json',
            success: function(data) {
                console.log('API 테스트 성공 - get-arrows-by-map:', data);
            },
            error: function(xhr, status, error) {
                console.error('API 테스트 실패 - get-arrows-by-map');
                console.error('상태 코드:', xhr.status);
                console.error('응답 텍스트:', xhr.responseText);
            }
        });
    }
}); 