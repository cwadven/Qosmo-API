### 5. 05_arrows.sql
노드 간의 진행 경로를 정의하는 arrows를 생성합니다.

테이블 명: map_arrow

**필수 필드:**
- map_id: 맵 식별자
- start_node_id: 시작 노드
- end_node_id: 도착 노드
- node_complete_rule_id: 다음 단계 완료 규칙 (end_node의 완료 규칙)
- question_id: null (일반 화살표는 question_id가 null)
- is_deleted: 삭제 여부
- created_at, updated_at: 생성/수정 시간

**Arrow 생성 규칙:**
1. 그룹 내부 연결
   - 같은 그룹 내의 노드들은 순차적 또는 병렬적으로 연결 가능
   - 순차적 연결: 이전 노드 완료 후 다음 노드로 진행
   - 병렬적 연결: 여러 시작 노드가 동일한 목표 노드로 연결 가능
   - node_complete_rule_id는 end_node의 완료 규칙을 지정

2. 그룹 간 연결
   - 한 그룹의 마지막 노드와 다음 그룹의 첫 노드를 연결
   - 이전 그룹 완료 후 다음 그룹 진행 가능
   - node_complete_rule_id는 end_node의 완료 규칙을 지정

3. 병렬 학습 경로
   - 여러 그룹에서 하나의 노드로 연결 가능 (예: 여러 고급 기능 -> 실전 프로젝트)
   - 각 화살표는 독립적인 진행 경로를 제공
  
# 노드 간 화살표 SQL 작성 규칙

## 작업 순서
1. 명확한 규칙 정리
   - 테이블 구조와 필드 정의 확인
   - 노드 간 참조 규칙 명확히 정의 (node_complete_rule_id는 end_node의 완료 규칙 참조)
   - 데이터 입력 규칙 정의

2. 작은 단위로 나누어 검증
   - 그룹 내부 연결 작성 및 검증
   - 그룹 간 연결 작성 및 검증
   - 병렬 학습 경로 설정 및 검증
   - 완료 규칙과 질문의 연관성 검증

3. 전체 검증 수행
   - 모든 필수 필드가 올바르게 설정되었는지 확인
   - 참조 관계가 일관되게 적용되었는지 검증
   - 학습 순서의 논리성 확인
   - SQL 문법과 포맷팅 검토

## 주의사항
- node_complete_rule_id는 반드시 도착 노드(end_node)의 완료 규칙을 참조
- 그룹 내부, 그룹 간 연결의 일관성 유지
- 병렬 학습이 가능한 경로 명확히 구분
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
)
INSERT INTO map_arrow (map_id, start_node_id, end_node_id, node_complete_rule_id, question_id, is_deleted, created_at, updated_at) VALUES
-- 그룹 내부 연결 예시
((SELECT id FROM map_id),
 (SELECT id FROM nodes WHERE name = '몽고소개'),
 (SELECT id FROM nodes WHERE name = '설치방법'),
 (SELECT id FROM complete_rules WHERE name = '설치방법'),
 null,
 false, NOW(), NOW()),

-- 그룹 간 연결 예시
((SELECT id FROM map_id),
 (SELECT id FROM nodes WHERE name = '쉘기초'),
 (SELECT id FROM nodes WHERE name = '도큐먼트구조'),
 (SELECT id FROM complete_rules WHERE name = '도큐먼트구조'),
 null,
 false, NOW(), NOW()),

-- 병렬 학습 경로 예시
((SELECT id FROM map_id),
 (SELECT id FROM nodes WHERE name = '복제설정'),
 (SELECT id FROM nodes WHERE name = '채팅서비스'),
 (SELECT id FROM complete_rules WHERE name = '채팅서비스'),
 null,
 false, NOW(), NOW()),

((SELECT id FROM map_id),
 (SELECT id FROM nodes WHERE name = '퍼블리시구독'),
 (SELECT id FROM nodes WHERE name = '채팅서비스'),
 (SELECT id FROM complete_rules WHERE name = '채팅서비스'),
 null,
 false, NOW(), NOW());
```

### 체크리스트

#### 0. 테이블

- [ ] map_arrow 로 insert 됨

#### 1. 필수 필드 체크리스트
- [ ] map_id: 맵 식별자가 올바르게 참조됨
- [ ] start_node_id: 시작 노드가 올바르게 참조됨
- [ ] end_node_id: 도착 노드가 올바르게 참조됨
- [ ] node_complete_rule_id: end_node의 완료 규칙이 올바르게 참조됨
  - [ ] 노드 간 연결 arrow도 node_complete_rule_id를 사용해야 함
  - [ ] 종료 노드의 complete rule을 사용하여 연결을 정의
- [ ] question_id: null로 설정됨
- [ ] is_deleted: false로 설정됨
- [ ] created_at, updated_at: NOW() 사용

#### 2. 그룹 내부 연결 체크리스트
- [ ] 그룹 내 노드들이 순차적/병렬적으로 적절히 연결됨
  - [ ] 순차적 진행이 필요한 노드들은 순서대로 연결
  - [ ] 병렬 진행이 가능한 노드들은 동일 목표 노드로 연결
- [ ] 각 화살표의 node_complete_rule_id가 end_node의 것으로 필수로 설정어야함
- [ ] 그룹 내 노드 간 연결이 학습 목표에 맞게 구성됨

#### 3. 그룹 간 연결 체크리스트
- [ ] 그룹의 마지막 노드와 다음 그룹의 첫 노드가 연결됨
- [ ] 그룹 간 연결이 학습 순서에 맞게 구성됨
- [ ] 그룹 간 선수 학습 관계가 명확히 표현됨
- [ ] 각 화살표의 node_complete_rule_id가 end_node의 것으로 설정됨

#### 4. 병렬 학습 경로 체크리스트
- [ ] 필요한 경우 여러 노드에서 하나의 노드로 연결됨
- [ ] 각 진행 경로가 독립적으로 구성됨
- [ ] 병렬 학습이 가능한 노드들이 적절히 식별됨
- [ ] 각 화살표의 node_complete_rule_id가 end_node의 것으로 설정됨

#### 5. SQL 작성 체크리스트
- [ ] WITH 구문에 필요한 모든 테이블 포함
  - [ ] map_id 서브쿼리
  - [ ] nodes 서브쿼리
  - [ ] complete_rules 서브쿼리
- [ ] INSERT 문법이 정확함
- [ ] SELECT 서브쿼리들이 올바르게 작성됨
- [ ] 모든 필드가 순서대로 입력됨
- [ ] 세미콜론으로 종료됨

#### 6. 가독성 체크리스트
- [ ] 적절한 들여쓰기 사용
- [ ] 그룹 구분 주석이 명확함
- [ ] SQL 문이 깔끔하게 포맷팅됨
- [ ] 불필요한 공백이나 주석이 없음
- [ ] 각 화살표의 목적이 명확히 드러남

#### 7. 논리성 체크리스트
- [ ] 전체 학습 흐름이 논리적으로 구성됨
- [ ] 선수 학습 관계가 올바르게 설정됨
- [ ] 학습 난이도가 적절히 고려됨
- [ ] 불필요한 화살표나 중복 경로가 없음
