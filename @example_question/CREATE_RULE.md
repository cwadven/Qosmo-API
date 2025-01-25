# SQL 파일 생성 규칙

## 파일 구조
맵 생성 시 다음 6개의 SQL 파일로 구성됩니다:

### 0. 00_map.sql
맵의 기본 정보를 설정합니다.

**필수 필드:**
- name: 맵 이름
- description: 맵 설명
- icon_image: 맵 아이콘 이미지 URL
- background_image: 맵 배경 이미지 URL
- subscriber_count: 구독자 수 (기본값 0)
- view_count: 조회수 (기본값 0)
- created_by_id: 생성자 ID (member_member 테이블 참조)
- categories: 카테고리 배열
- is_private: 비공개 여부
- is_deleted: 삭제 여부
- created_at, updated_at: 생성/수정 시간

예제:
```sql
INSERT INTO map_map (
  name, description, icon_image, background_image,
  subscriber_count, view_count, created_by_id,
  is_private, is_deleted,
  created_at, updated_at
) VALUES (
  'Process Guide Map',
  'A comprehensive guide for our development process',
  'https://placehold.co/600x400',
  'https://placehold.co/600x400',
  0,
  0,
  (SELECT id FROM member_member WHERE username = 'admin' LIMIT 1),
  false,
  false,
  NOW(),
  NOW()
) RETURNING id;
```

**참고:**
- icon_image와 background_image는 placeholder 이미지 사용
- created_by_id는 실제 존재하는 member_member의 id 사용
- categories는 적절한 키워드 배열로 설정
- 생성된 map_id를 이후 다른 SQL 파일에서 참조

### 1. 01_nodes.sql
노드의 기본 정보와 위치를 설정합니다.

**필수 필드:**
- map_id: 맵 식별자
- name: 노드의 고유 식별자 (한글)
- title: 표시될 제목
- description: 설명
- background_image: 노드 배경 이미지 URL
- position_x, position_y: 노드 위치 좌표
- width, height: 노드 크기
- is_deleted: 삭제 여부
- created_at, updated_at: 생성/수정 시간

**노드 배치 규칙:**
- 노드 최소 개수: 30개 이상 필수
- 기본 노드 크기: width 150, height 100
- 노드 간 최소 간격: 가로 300px, 세로 300px
- 노드 중첩 방지를 위해 width/height 고려하여 좌표 설정
- 연관된 노드는 같은 y축 값에 배치 권장
- 노드가 많을 경우 y축 값을 300px 간격으로 구분하여 그룹화
- 한 줄(y축)에 너무 많은 노드가 있을 경우 가독성을 위해 분리 권장

**name 필드 작성 규칙:**
- 한글로 작성
- 의미를 명확히 전달할 수 있는 이름 사용
- 동일 맵 내에서 중복되지 않도록 주의
- 가능한 간단명료하게 작성

예제:
```sql
WITH map_id AS (
  SELECT id FROM map_map WHERE name = 'Process Guide Map'
)
INSERT INTO map_node (map_id, name, title, description, background_image, position_x, position_y, width, height, is_deleted, created_at, updated_at) VALUES
((SELECT id FROM map_id), '시작_지점', '시작 지점', '프로세스의 시작점입니다.', 'https://placehold.co/600x400', 100, 100, 150, 100, false, NOW(), NOW()),
((SELECT id FROM map_id), '다음_지점', '다음 지점', '두 번째 단계입니다.', 'https://placehold.co/600x400', 400, 100, 150, 100, false, NOW(), NOW()),
((SELECT id FROM map_id), '그룹1_노드1', '그룹1 노드1', '첫 번째 그룹의 노드입니다.', 'https://placehold.co/600x400', 700, 100, 150, 100, false, NOW(), NOW()),
((SELECT id FROM map_id), '그룹2_노드1', '그룹2 노드1', '두 번째 그룹의 노드입니다.', 'https://placehold.co/600x400', 100, 400, 150, 100, false, NOW(), NOW());
```

### 2. 02_node_complete_rules.sql
각 노드의 완료 조건을 정의합니다.

**필수 필드:**
- map_id: 맵 식별자
- name: 규칙 이름
- description: 규칙 설명
- is_deleted: 삭제 여부
- created_at, updated_at: 생성/수정 시간

**규칙 설정:**
- 모든 노드는 최소 1개 이상의 complete rule을 가져야 함
- 필요한 경우 노드 당 여러 개의 complete rule 설정 가능
- name은 해당 활동을 명확히 설명하는 직관적인 이름 사용
- description은 사용자가 이해하기 쉽게 상세히 작성

예제:
```sql
WITH map_id AS (
  SELECT id FROM map_map WHERE name = 'Process Guide Map'
)
INSERT INTO map_nodecompleterule (map_id, name, description, is_deleted, created_at, updated_at) VALUES
((SELECT id FROM map_id), '초기 설정 완료', '시작 단계에서 필요한 기본 설정을 완료하세요.', false, NOW(), NOW()),
((SELECT id FROM map_id), '문서 작성 완료', '프로젝트 문서 초안을 작성하세요.', false, NOW(), NOW()),
((SELECT id FROM map_id), '문서 검토 완료', '작성된 문서의 검토를 완료하세요.', false, NOW(), NOW());
```

### 3. 03_questions.sql
노드 완료를 검증하기 위한 질문을 생성합니다.

**필수 필드:**
- map_id: 맵 식별자
- title: 질문 제목
- description: 질문 내용
- question_types: 입력 유형 (ARRAY['text', 'file'])
- answer_validation_type: 답변 검증 방식
- is_by_pass: 검증 우회 가능 여부
- default_success_feedback: 성공 시 메시지
- default_failure_feedback: 실패 시 메시지
- is_deleted: 삭제 여부
- created_at, updated_at: 생성/수정 시간

**질문 작성 규칙:**
- 모든 노드는 최소 1개 이상의 질문을 가져야 함
- 모든 노드는 반드시 자신의 완료를 검증하기 위한 질문을 가져야 함 (필수)
- 노드의 개수만큼 질문이 존재해야 함 (1:1 매칭)
- 04_self_arrows.sql 에 적용될 수 있게 질문 제목은 해당 노드의 title과 연관성 있게 작성
- 질문은 해당 노드의 완료 조건을 검증할 수 있어야 함
- 모든 질문은 반드시 text와 file 두 가지 입력 타입 포함 (ARRAY['text', 'file'])
- answer_validation_type은 'manual'로 설정 (영문 소문자)
- description은 한글로 작성
- 피드백 메시지는 긍정적이고 명확하게 작성
- 질문 제목은 해당 노드의 title과 연관성 있게 작성
- description 안에 있는 질문은 1개의 질문으로 구성

예제:
```sql
WITH map_id AS (
  SELECT id FROM map_map WHERE name = 'Process Guide Map'
)
INSERT INTO question_question (map_id, title, description, question_types, answer_validation_type, is_by_pass, default_success_feedback, default_failure_feedback, is_deleted, created_at, updated_at) VALUES
((SELECT id FROM map_id), 'Initial Setup Check', 'Please verify your initial setup is complete.', ARRAY['text', 'file'], 'manual', true, 'Great job! Setup is complete.', 'Please complete all setup steps.', false, NOW(), NOW()),
((SELECT id FROM map_id), 'Document Review Check', 'Please upload the reviewed document and add your comments.', ARRAY['text', 'file'], 'manual', true, 'Perfect! Document review is complete.', 'Please complete the document review.', false, NOW(), NOW());
```

### 4. 04_self_arrows.sql
노드의 완료 상태를 체크하는 self-referencing arrows를 생성합니다.

**필수 필드:**
- map_id: 맵 식별자
- start_node_id: 시작 노드 (자기 자신)
- end_node_id: 도착 노드 (자기 자신)
- node_complete_rule_id: 완료 규칙
- question_id: 검증 질문 (필수)
- is_deleted: 삭제 여부
- created_at, updated_at: 생성/수정 시간

**Self-arrows 생성 규칙:**
- 모든 노드는 반드시 자신을 가리키는 self-arrow를 가져야 함 (필수)
- 노드의 개수만큼 self-arrow가 존재해야 함 (1:1 매칭)
- 각 self-arrow는 해당 노드의 완료 규칙과 검증 질문을 반드시 연결해야 함
- start_node_id와 end_node_id는 동일한 노드를 가리켜야 함
- question_id는 반드시 지정되어야 함 (null 불가)
- 해당 노드의 완료 조건을 검증하는 질문과 연결되어야 함

예제:
```sql
WITH map_id AS (
  SELECT id FROM map_map WHERE name = 'Process Guide Map'
)
-- 모든 노드에 대해 self-arrow를 생성해야 함
INSERT INTO map_arrow (map_id, start_node_id, end_node_id, node_complete_rule_id, question_id, is_deleted, created_at, updated_at) VALUES
((SELECT id FROM map_id),
 (SELECT id FROM map_node WHERE map_id = (SELECT id FROM map_id) AND name = '시작_지점'),
 (SELECT id FROM map_node WHERE map_id = (SELECT id FROM map_id) AND name = '시작_지점'),
 (SELECT id FROM map_nodecompleterule WHERE map_id = (SELECT id FROM map_id) AND name = '초기 설정 완료'),
 (SELECT id FROM question_question WHERE map_id = (SELECT id FROM map_id) AND title = '초기 설정 확인'),
 false, NOW(), NOW()),
... (다른 모든 노드들에 대해서도 동일하게 생성);
```

### 5. 05_path_arrows.sql
노드 간의 진행 경로를 정의하는 arrows를 생성합니다.

**필수 필드:**
- map_id: 맵 식별자
- start_node_id: 시작 노드
- end_node_id: 도착 노드
- node_complete_rule_id: 다음 단계 완료 규칙
- question_id: null
- is_deleted: 삭제 여부
- created_at, updated_at: 생성/수정 시간

예제:
```sql
WITH map_id AS (
  SELECT id FROM map_map WHERE name = 'Process Guide Map'
)
INSERT INTO map_arrow (map_id, start_node_id, end_node_id, node_complete_rule_id, question_id, is_deleted, created_at, updated_at) VALUES
((SELECT id FROM map_id),
 (SELECT id FROM map_node WHERE map_id = (SELECT id FROM map_id) AND name = '시작_지점'),
 (SELECT id FROM map_node WHERE map_id = (SELECT id FROM map_id) AND name = '다음_지점'),
 (SELECT id FROM map_nodecompleterule WHERE map_id = (SELECT id FROM map_id) AND name = '다음 단계 준비'),
 null,
 false, NOW(), NOW());
```

## 공통 규칙
1. 모든 SQL 파일은 INSERT 문으로 구성
2. is_deleted 필드로 삭제 여부 관리
3. created_at, updated_at으로 시간 관리
4. 외래 키는 SELECT 서브쿼리로 참조
5. map_id는 WITH 절을 사용하여 참조


**참고:**
- 모든 SQL 파일에서 map_id를 직접 숫자로 입력하지 않고 WITH 절로 조회
- map_id가 필요한 모든 서브쿼리에서 WITH 절의 map_id 재사용
- 맵 이름으로 식별하여 map_id 조회

## Arrow 생성 규칙
1. Self-referencing arrows (04_self_arrows.sql)
   - 노드 자신을 가리키는 화살표
   - 해당 노드의 완료 규칙과 검증 질문 연결
   - question_id 필수

2. Path arrows (05_path_arrows.sql)
   - 노드 간 진행 경로 표시
   - 다음 단계의 완료 규칙 연결
   - question_id는 null


## 기록용

[ 생성 ]

docker cp ./@example_question/파이썬초보탈출 checker_postgresql14:/home/

psql -U postgres -d checker_database -f /home/파이썬초보탈출/00_map.sql
psql -U postgres -d checker_database -f /home/파이썬초보탈출/01_nodes.sql
psql -U postgres -d checker_database -f /home/파이썬초보탈출/02_node_complete_rules.sql
psql -U postgres -d checker_database -f /home/파이썬초보탈출/03_questions.sql
psql -U postgres -d checker_database -f /home/파이썬초보탈출/04_self_arrows.sql
psql -U postgres -d checker_database -f /home/파이썬초보탈출/05_arrows.sql

psql -U postgres -d qosmo_database -f 00_map.sql
psql -U postgres -d qosmo_database -f 01_nodes.sql
psql -U postgres -d qosmo_database -f 02_node_complete_rules.sql
psql -U postgres -d qosmo_database -f 03_questions.sql
psql -U postgres -d qosmo_database -f 04_self_arrows.sql
psql -U postgres -d qosmo_database -f 05_arrows.sql


[ 초기화 ]

delete from map_arrow where map_id != 2;
delete from map_nodecompleterule where map_id != 2;
delete from map_node where map_id != 2;
delete from question_question where map_id != 2;
delete from map_mapcategory where map_id != 2;
delete from map_map where id != 2;
