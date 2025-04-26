### 2. 02_node_complete_rules.sql
노드의 완료 규칙을 설정합니다.

테이블 명: map_nodecompleterule

**필수 필드:**
- map_id: 맵 식별자
- node_id: 노드 식별자
- name: 문제 완료 규칙 이름
- is_deleted: 삭제 여부
- created_at, updated_at: 생성/수정 시간

**name 필드 작성 규칙:**
- 01_nodes.sql에서 정의한 노드의 name과 정확히 일치해야 함
- 한글로 작성
- 중복 불가

**SQL 작성 예시:**
```sql
WITH map_id AS (
  SELECT id FROM map_map WHERE name = '연인과 여행 데이트'
)
INSERT INTO map_nodecompleterule (map_id, node_id, name, is_deleted, created_at, updated_at) VALUES
((SELECT id FROM map_id), (SELECT id FROM map_node WHERE map_id = (SELECT id FROM map_id) AND name = '시작 지점'), '여행 스타일 정리', false, NOW(), NOW());
```

### 체크리스트

#### 0. 테이블

- [ ] map_nodecompleterule 로 insert 됨

#### 1. 필수 필드 체크리스트
- [ ] map_id: 맵 식별자가 올바르게 참조됨
- [ ] node_id: 노드 식별자가 올바르게 참조됨
- [ ] name: 노드 완료를 위한 규칙 이름이 명확함
- [ ] is_deleted: false로 설정됨
- [ ] created_at: NOW() 함수 사용
- [ ] updated_at: NOW() 함수 사용

#### 2. name 필드 규칙 체크리스트
- [ ] 해당 노드의 완료 조건을 명확히 설명하는 이름
- [ ] 한글로만 작성됨
- [ ] 맵 내에서 중복되지 않음
- [ ] 특수문자나 영문 미포함
- [ ] 완료 규칙의 목적이 이름에서 명확히 드러남
예) '몽고디비 이해 완료', '설치 확인 완료', '기본 명령어 실습 완료'

#### 3. 참조 무결성 체크리스트
- [ ] map_id가 실제 존재하는 맵을 참조
- [ ] node_id가 실제 존재하는 노드를 참조
- [ ] 모든 노드에 대한 완료 규칙이 존재
- [ ] 노드와 완료 규칙이 1:1로 매칭됨

#### 4. SQL 작성 체크리스트
- [ ] WITH map_id AS 구문이 올바름
- [ ] INSERT 문법이 정확함
- [ ] SELECT 서브쿼리가 올바르게 작성됨
- [ ] 모든 필드가 순서대로 입력됨
- [ ] 값들이 적절한 따옴표로 감싸짐
- [ ] 세미콜론으로 종료됨

#### 5. 가독성 체크리스트
- [ ] 적절한 들여쓰기 사용
- [ ] 그룹 구분 주석이 명확함
- [ ] SQL 문이 깔끔하게 포맷팅됨
- [ ] 불필요한 공백이나 주석이 없음
- [ ] 각 완료 규칙의 목적이 이름에서 명확히 드러남
