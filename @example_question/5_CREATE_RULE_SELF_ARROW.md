### 4. 04_self_arrows.sql
노드의 완료 상태를 체크하는 self-referencing arrows를 생성합니다.

테이블 명: map_arrow

**필수 필드:**
- map_id: 맵 식별자
- start_node_id: 시작 노드 (자기 자신)
- end_node_id: 도착 노드 (자기 자신)
- node_complete_rule_id: 완료 규칙
- question_id: 검증 질문 (필수, 중복 불가)
- is_deleted: 삭제 여부
- created_at, updated_at: 생성/수정 시간

**Self-arrows 생성 규칙:**
- 모든 노드는 반드시 자신을 가리키는 self-arrow를 가져야 함 (필수, 1개 이상)
- 각 self-arrow는 해당 노드의 완료 규칙과 검증 질문을 반드시 연결해야 함
- start_node_id와 end_node_id는 동일한 노드를 가리켜야 함
- question_id는 반드시 지정되어야 하며 중복될 수 없음 (null 불가, unique)
- 해당 노드의 완료 조건을 검증하는 질문과 연결되어야 함

# 자기 참조 화살표 SQL 작성 규칙

## 작업 순서
1. 명확한 규칙 정리
   - 테이블 구조와 필드 정의 확인
   - 자기 참조 규칙 명확히 정의 (node_complete_rule_id는 해당 노드 자신의 완료 규칙 참조)
   - 데이터 입력 규칙 정의

2. 작은 단위로 나누어 검증
   - 그룹별로 나누어 작성 및 검증
   - 각 노드의 자기 참조 규칙 확인
   - 완료 규칙과 질문의 연관성 검증

3. 전체 검증 수행
   - 모든 필수 필드가 올바르게 설정되었는지 확인
   - 자기 참조가 일관되게 적용되었는지 검증
   - SQL 문법과 포맷팅 검토

## 주의사항
- 자기 참조는 항상 동일한 노드를 start_node와 end_node로 사용
- 해당 노드의 완료 규칙을 정확히 참조
- 대량의 데이터 처리 시 체계적인 검증 필요 

예제:
```sql
WITH map_id AS (
  SELECT id FROM map_map WHERE name = 'NoSQL 시작하기'
),
nodes AS (
  SELECT id, name 
  FROM map_node 
  WHERE map_id = (SELECT id FROM map_id)
),
complete_rules AS (
  SELECT id, name
  FROM map_nodecompleterule 
  WHERE map_id = (SELECT id FROM map_id)
),
questions AS (
  SELECT id, title
  FROM question_question 
  WHERE map_id = (SELECT id FROM map_id)
)
INSERT INTO map_arrow (map_id, start_node_id, end_node_id, node_complete_rule_id, question_id, is_deleted, created_at, updated_at) VALUES
((SELECT id FROM map_id),
 (SELECT id FROM nodes WHERE name = '몽고소개'),
 (SELECT id FROM nodes WHERE name = '몽고소개'),
 (SELECT id FROM complete_rules WHERE name = '몽고디비이해완료'),
 (SELECT id FROM questions WHERE title = 'MongoDB 개념 이해도 확인'),
 false, NOW(), NOW());
```

### 체크리스트

#### 0. 테이블

- [ ] map_arrow 로 insert 됨

#### 1. 필수 필드 체크리스트
- [ ] map_id: 맵 식별자가 올바르게 참조됨
- [ ] start_node_id: 시작 노드가 올바르게 참조됨
- [ ] end_node_id: 도착 노드가 올바르게 참조됨
- [ ] node_complete_rule_id: 완료 규칙이 올바르게 참조됨
- [ ] question_id: 검증 질문이 올바르게 참조됨 (null 불가, 중복 불가)
- [ ] is_deleted: false로 설정됨
- [ ] created_at, updated_at: NOW() 사용

#### 2. 참조 무결성 체크리스트
- [ ] start_node_id와 end_node_id가 동일한 노드를 가리킴
- [ ] 모든 노드에 대한 self-arrow가 1개 이상 존재
- [ ] node_complete_rule_id가 해당 노드의 완료 규칙을 가리킴
- [ ] question_id가 해당 노드의 검증 질문을 가리킴

#### 3. SQL 작성 체크리스트
- [ ] WITH 구문에 필요한 모든 테이블 포함
  - [ ] map_id 서브쿼리
  - [ ] nodes 서브쿼리
  - [ ] complete_rules 서브쿼리
  - [ ] questions 서브쿼리
- [ ] INSERT 문법이 정확함
- [ ] SELECT 서브쿼리들이 올바르게 작성됨
- [ ] 모든 필드가 순서대로 입력됨
- [ ] 세미콜론으로 종료됨

#### 4. 가독성 체크리스트
- [ ] 적절한 들여쓰기 사용
- [ ] 그룹 구분 주석이 명확함
- [ ] SQL 문이 깔끔하게 포맷팅됨
- [ ] 불필요한 공백이나 주석이 없음
- [ ] 각 self-arrow의 목적이 명확히 드러남

#### 5. 논리성 체크리스트
- [ ] 각 노드의 완료 조건이 적절히 검증됨
- [ ] 완료 규칙과 검증 질문이 논리적으로 연결됨
- [ ] self-arrow가 노드의 학습 목표를 반영함
- [ ] 검증 질문이 완료 규칙을 충족하는지 확인할 수 있음
