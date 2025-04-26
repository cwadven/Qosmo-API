// QuestionAnswer 모델 관리자 페이지용 스크립트
window.addEventListener('load', function () {
    // 가능한 모든 jQuery 참조 시도
    var jq = window.jQuery || window.django && window.django.jQuery || (typeof django !== 'undefined' && django.jQuery);
    
    if (jq) {
        console.log('jQuery를 찾았습니다!');
        initQuestionAnswerAdmin(jq);
    } else {
        // 500ms마다 jQuery를 찾아보기
        console.log('Django 관리자 페이지의 jQuery를 기다립니다...');
        var attempts = 0;
        var checkInterval = setInterval(function () {
            attempts++;
            jq = window.jQuery || window.django && window.django.jQuery || (typeof django !== 'undefined' && django.jQuery);
            
            if (jq) {
                console.log('jQuery를 찾았습니다! (시도 횟수: ' + attempts + ')');
                clearInterval(checkInterval);
                initQuestionAnswerAdmin(jq);
            }
            
            if (attempts >= 10) {
                console.error('10번 시도 후에도 jQuery를 찾지 못했습니다.');
                clearInterval(checkInterval);
            }
        }, 500);
    }
});

function initQuestionAnswerAdmin($) {
    console.log('QuestionAnswer admin 스크립트 초기화');
    
    if ($('#id_question').length > 0) {
        console.log('QuestionAnswer admin form 감지됨');
        
        // 처음 페이지 로딩 시 초기 상태 저장
        var initialQuestionId = $('#id_question').val();
        console.log('Question ID 현재 값:', initialQuestionId);
        
        // 질문이 이미 선택되어 있다면 관련 정보 로드
        if (initialQuestionId) {
            console.log('이미 선택된 Question ID가 있어 질문 정보를 로드합니다:', initialQuestionId);
            
            // AJAX 요청 - 질문 정보 가져오기
            $.ajax({
                url: '/v1/map-admin/get-question-info',
                data: {
                    'question_id': initialQuestionId
                },
                dataType: 'json',
                success: function (data) {
                    console.log('질문 정보 로드됨:', data);
                    // 질문 정보를 표시 (제목, 설명 등)
                    if (data.title) {
                        displayQuestionInfo(data);
                    }
                },
                error: function (xhr, status, error) {
                    console.error('질문 정보를 가져오는 중 오류 발생:', error);
                    console.error('상태 코드:', xhr.status);
                    console.error('응답 텍스트:', xhr.responseText);
                }
            });
        }

        $('#id_map').on('change', function () {
            var mapId = $(this).val();
            console.log('Map 변경됨:', mapId);
            clearQuestionInfo();

            // AJAX 요청 - 질문 정보 가져오기
            $.ajax({
                url: '/v1/map-admin/get-questions-by-map',
                data: {
                    'map_id': mapId,
                },
                dataType: 'json',
                success: function (data) {
                    console.log('질문 정보 리스트 로드됨:', data);
                    var options = '<option value="">---------</option>';
                    $.each(data, function(index, item) {
                        options += '<option value="' + item.id + '">' + item.title + '</option>';
                    });
                    $('#id_question').html(options);
                },
                error: function (xhr, status, error) {
                    console.error('질문 정보 리스트를 가져오는 중 오류 발생:', error);
                    console.error('상태 코드:', xhr.status);
                    console.error('응답 텍스트:', xhr.responseText);
                }
            });
        });
        
        // 질문 변경 시 이벤트 핸들러
        $('#id_question').on('change', function () {
            var questionId = $(this).val();
            console.log('Question 변경됨:', questionId);
            
            if (!questionId) {
                // 질문이 선택되지 않은 경우, 관련 표시 초기화
                clearQuestionInfo();
                return;
            }
            
            // AJAX 요청 - 질문 정보 가져오기
            $.ajax({
                url: '/v1/map-admin/get-question-info',
                data: {
                    'question_id': questionId
                },
                dataType: 'json',
                success: function (data) {
                    console.log('질문 정보 로드됨:', data);
                    displayQuestionInfo(data);
                },
                error: function (xhr, status, error) {
                    console.error('질문 정보를 가져오는 중 오류 발생:', error);
                    console.error('상태 코드:', xhr.status);
                    console.error('응답 텍스트:', xhr.responseText);
                }
            });
        });
    }
    
    // 질문 정보 표시 함수
    function displayQuestionInfo(questionData) {
        // 이미 사용자 정의 정보 표시 영역이 있는지 확인
        var infoContainer = $('#question-info-container');
        if (infoContainer.length === 0) {
            // 없으면 새로 생성
            infoContainer = $('<div id="question-info-container" class="question-info"></div>');
            $('#id_question').after(infoContainer);
        }
        
        // 질문 정보 표시
        var infoHtml = '<div class="info-box">';
        infoHtml += '<h4>선택된 질문 정보</h4>';
        infoHtml += '<p><strong>제목:</strong> ' + questionData.title + '</p>';
        
        if (questionData.description) {
            infoHtml += '<p><strong>설명:</strong> ' + questionData.description + '</p>';
        }
        
        if (questionData.question_types && questionData.question_types.length > 0) {
            infoHtml += '<p><strong>문제 유형:</strong> ' + questionData.question_types.join(', ') + '</p>';
        }
        
        if (questionData.map_name) {
            infoHtml += '<p><strong>맵:</strong> ' + questionData.map_name + '</p>';
        }
        
        infoHtml += '</div>';
        infoContainer.html(infoHtml);
    }
    
    // 질문 정보 초기화 함수
    function clearQuestionInfo() {
        $('#question-info-container').empty();
    }
}