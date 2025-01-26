### 1. 01_nodes.sql
노드의 기본 정보와 위치를 설정합니다.

테이블명: map_node

**필수 필드:**
- map_id: 맵 식별자
- name: 노드의 고유 식별자 (한글), 같은 맵에서 중복 없어야함
- title: 표시될 제목
- description: 설명
- background_image: 노드 배경 이미지 URL
- position_x, position_y: 노드 위치 좌표
- width, height: 노드 크기
- is_active: 활성 여부 항상 true
- is_deleted: 삭제 여부
- created_at, updated_at: 생성/수정 시간

**name 필드 작성 규칙:**
이 규칙은 map_node의 name 필드에만 적용됩니다.

1. **한글 필수**
   - map_node의 name 필드는 반드시 한글로 작성
   - 영문이나 특수문자 사용 금지
   - 예시: 'travel_style' (❌) → '여행스타일' (⭕)

2. **명확성**
   - 의미를 명확히 전달할 수 있는 이름 사용
   - 축약어 사용 지양
   - 예시: '여행지선정' (❌) → '여행지' (⭕)

3. **중복 방지**
   - 동일 맵 내에서 절대로 name 이 중복되지 않도록 주의
   - 다른 노드와 구분되는 고유한 이름 사용

4. **간결성**
   - 가능한 간단명료하게 작성
   - 불필요한 수식어 제외
   - 예시: '아침식사데이트코스' (❌) → '아침식사' (⭕)

**노드 배치 규칙:**
- 노드 최소 개수: 30개 이상 필수
- 기본 노드 크기: width 150, height 100
- 노드 간 최소 간격: 가로 300px, 세로 300px
- 노드 중첩 방지를 위해 width/height 고려하여 좌표 설정
- 연관된 노드는 같은 y축 값에 배치 권장
- 노드가 많을 경우 y축 값을 300px 간격으로 구분하여 그룹화
- 한 줄(y축)에 너무 많은 노드가 있을 경우 가독성을 위해 분리 권장

예제:
```sql
WITH map_id AS (
  SELECT id FROM map_map WHERE name = '연인과 여행 데이트'
)
INSERT INTO map_node (map_id, name, title, description, background_image, position_x, position_y, width, height, is_active, is_deleted, created_at, updated_at) VALUES
((SELECT id FROM map_id), '시작_지점', '시작 지점', '프로세스의 시작점입니다.', 'https://placehold.co/600x400', 100, 100, 150, 100, true, false, NOW(), NOW()),
((SELECT id FROM map_id), '다음_지점', '다음 지점', '두 번째 단계입니다.', 'https://placehold.co/600x400', 400, 100, 150, 100, true, false, NOW(), NOW()),
((SELECT id FROM map_id), '그룹1_노드1', '그룹1 노드1', '첫 번째 그룹의 노드입니다.', 'https://placehold.co/600x400', 700, 100, 150, 100, true, false, NOW(), NOW()),
((SELECT id FROM map_id), '그룹2_노드1', '그룹2 노드1', '두 번째 그룹의 노드입니다.', 'https://placehold.co/600x400', 100, 400, 150, 100, true, false, NOW(), NOW());
```

### 체크리스트

#### 0. 테이블

- [ ] map_node 로 insert 됨

#### 1. 필수 필드 체크리스트
- [ ] map_id: 맵 식별자가 올바르게 참조됨
- [ ] name: 한글로 작성되었으며 중복 없음
- [ ] title: 노드 제목이 명확함
- [ ] description: 노드 설명이 충분함
- [ ] background_image: 올바른 URL 형식
- [ ] position_x, position_y: 규칙에 맞는 좌표값
- [ ] width: 150px로 통일
- [ ] height: 100px로 통일
- [ ] is_active: true로 설정
- [ ] is_deleted: false로 설정
- [ ] created_at, updated_at: NOW() 사용

#### 2. name 필드 규칙 체크리스트
- [ ] 모든 name이 한글로만 작성됨
- [ ] 영문/특수문자가 포함되지 않음
- [ ] 의미가 명확하게 전달됨
- [ ] 축약어를 사용하지 않음
- [ ] 맵 내에서 중복된 이름이 없음
- [ ] 불필요한 수식어가 없음

#### 3. 노드 배치 체크리스트
- [ ] 총 노드 수가 50개 이상임
- [ ] 모든 노드의 크기가 150x100으로 통일됨
- [ ] 가로 간격이 300px 이상 유지됨
- [ ] 세로 간격이 300px 이상 유지됨
- [ ] 연관된 노드들 끼리 같은 그룹에 배치됨
- [ ] 그룹별로 x축 혹은 y축  500px 간격으로 구분됨

#### 4. SQL 작성 체크리스트
- [ ] WITH map_id AS 구문이 올바름
- [ ] INSERT 문법이 정확함
- [ ] 각 그룹이 주석으로 구분됨
- [ ] 모든 필드가 순서대로 입력됨
- [ ] 값들이 적절한 따옴표로 감싸짐
- [ ] NOW() 함수가 올바르게 사용됨
- [ ] 세미콜론으로 종료됨

#### 5. 가독성 체크리스트
- [ ] 적절한 들여쓰기 사용
- [ ] 그룹 구분 주석이 명확함
- [ ] SQL 문이 깔끔하게 포맷팅됨
- [ ] 각 노드의 목적이 명확히 설명됨
- [ ] 불필요한 공백이나 주석이 없음
