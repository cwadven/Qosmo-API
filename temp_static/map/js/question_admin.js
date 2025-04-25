// Question 모델 관리자 페이지용 스크립트
window.addEventListener('load', function() {
    // 가능한 모든 jQuery 참조 시도
    var jq = window.jQuery || window.django && window.django.jQuery || (typeof django !== 'undefined' && django.jQuery);
    
    if (jq) {
        console.log('jQuery를 찾았습니다!');
        initQuestionAdmin(jq);
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
                initQuestionAdmin(jq);
            }
            
            if (attempts >= 10) {
                console.error('10번 시도 후에도 jQuery를 찾지 못했습니다.');
                clearInterval(checkInterval);
            }
        }, 500);
    }
});

function initQuestionAdmin($) {
    console.log('Question admin 스크립트 초기화');
    
    if ($('#id_map').length > 0) {
        console.log('Question admin form 감지됨');
        
        // 처음 페이지 로딩 시 초기 상태 저장
        console.log('Map ID 현재 값:', $('#id_map').val());
        
        // Map 필드가 변경될 때 이벤트 처리는 필요 없음
        // Question 모델은 Map과 연관된 다른 필드가 현재 없음
    }
} 