### 3. 03_questions.sql
노드 완료를 검증하기 위한 질문을 생성합니다.

테이블 명: question_question

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
- 모든 노드는 최소 2개 이상의 질문을 가져야 함
- 모든 노드는 반드시 자신의 완료를 검증하기 위한 질문을 가져야 함 (필수)
- 노드의 개수만큼 질문이 존재해야 함 (1:N 매칭, N>=2)
- 04_self_arrows.sql 에 적용될 수 있게 질문 제목은 해당 노드의 title과 연관성 있게 작성
- 질문은 해당 노드의 완료 조건을 검증할 수 있어야 함
- 모든 질문은 반드시 text와 file 두 가지 입력 타입 포함 (ARRAY['text', 'file'])
- answer_validation_type은 'manual'로 설정 (영문 소문자)
- description은 한글로 작성
- 피드백 메시지는 긍정적이고 명확하게 작성
- 질문 제목은 해당 노드의 title과 연관성 있게 작성
- description 안에 있는 질문은 1개의 질문으로 구성
- self-arrow에 사용될 질문은 다른 self-arrow에서 중복 사용될 수 없음
- 단순 질문형보다는 행동 유도형으로 작성
  - ❌ "MongoDB의 주요 특징과 장점을 설명해주세요."
  - ⭕ "제공된 MongoDB 공식 문서를 읽고 주요 특징 중 가장 중요하다고 생각하는 3가지를 작성해주세요."
- 질문과 함께 참고할 수 있는 자료를 반드시 제공
  - 공식 문서 링크
  - 튜토리얼 사이트
  - 예제 코드
  - 관련 블로그 포스트
- 학습자가 수행해야 할 작업을 명확하게 제시
  - ❌ "MongoDB 설치 방법에 대해 설명해주세요."
  - ⭕ "공식 사이트의 설치 가이드를 따라 MongoDB를 설치하고, 설치 과정에서 겪은 문제와 해결 방법을 공유해주세요."
- 복잡한 개념은 작은 단계로 나누어 접근
  - ❌ "MongoDB의 인덱싱 전략을 설명해주세요."
  - ⭕ "1) 제공된 예제 데이터베이스에서 가장 자주 조회되는 필드를 찾아보세요.
        1) 해당 필드에 인덱스를 적용해보세요.
        2) 실행 계획을 비교하여 성능 향상을 확인해주세요."
- 실제 상황에서 적용할 수 있는 실습 위주로 구성
  - ❌ "트랜잭션의 개념에 대해 설명해주세요."
  - ⭕ "제공된 온라인 쇼핑몰 예제에서 주문 처리 과정에 트랜잭션을 적용하고, 결과를 공유해주세요." 

예제:
```sql
WITH map_id AS (
  SELECT id FROM map_map WHERE name = '연인과 여행 데이트'
)
INSERT INTO question_question (
    map_id,
    title,
    description,
    question_types,
    answer_validation_type,
    is_by_pass,
    default_success_feedback,
    default_failure_feedback,
    is_deleted,
    created_at,
    updated_at
) VALUES
-- 여행 준비 그룹
((SELECT id FROM map_id),
 '여행 스타일 파악',
 '연인과 함께 선호하는 여행 스타일을 정리해주세요. (예: 관광지 중심, 휴양, 맛집 탐방 등)',
 ARRAY['text', 'file'],
 'manual',
 true,
 '여행 스타일을 잘 정리하셨네요!',
 null,
 false, NOW(), NOW());
```

### 체크리스트

#### 0. 테이블

- [ ] question_question 로 insert 됨

#### 1. 필수 필드 체크리스트
- [ ] map_id: 맵 식별자가 올바르게 참조됨
- [ ] title: 질문 제목이 명확함, 각 question 들과 중첩된 내용이 있으면 안됨
- [ ] description: 질문 내용이 구체적임
- [ ] question_types: ARRAY['text', 'file'] 포함
- [ ] answer_validation_type: 'manual'로 설정
- [ ] is_by_pass: true로 설정
- [ ] default_success_feedback: 긍정적인 피드백 메시지
- [ ] default_failure_feedback: null로 설정
- [ ] is_deleted: false로 설정
- [ ] created_at, updated_at: NOW() 사용

#### 2. 질문 내용 체크리스트
- [ ] 노드당 최소 2개 이상의 질문 존재
- [ ] 노드의 완료 조건을 검증할 수 있는 내용
- [ ] description이 한글로 작성됨
- [ ] description 내 질문이 1개로 구성됨
- [ ] 질문이 구체적이고 명확함
- [ ] 해당 노드의 학습 목표를 반영

#### 3. 제목 및 연관성 체크리스트
- [ ] title이 해당 노드의 title과 연관성 있음
- [ ] 질문의 목적이 제목에서 명확히 드러남
- [ ] 04_self_arrows.sql과의 연계성 고려
- [ ] 노드와 질문이 1:N(N>=2) 매칭됨

#### 4. SQL 작성 체크리스트
- [ ] WITH map_id AS 구문이 올바름
- [ ] INSERT 문법이 정확함
- [ ] 모든 필드가 순서대로 입력됨
- [ ] 값들이 적절한 따옴표로 감싸짐
- [ ] 배열 타입이 올바르게 지정됨
- [ ] 세미콜론으로 종료됨

#### 5. 가독성 체크리스트
- [ ] 적절한 들여쓰기 사용
- [ ] 그룹 구분 주석이 명확함
- [ ] SQL 문이 깔끔하게 포맷팅됨
- [ ] 불필요한 공백이나 주석이 없음
- [ ] 각 질문의 목적이 명확히 드러남

#### 6. 피드백 메시지 체크리스트
- [ ] 성공 피드백이 긍정적으로 작성됨
- [ ] 성공 피드백이 구체적이고 명확함
- [ ] 실패 피드백이 null로 설정됨
- [ ] 피드백이 학습 동기를 부여하는 내용
- [ ] 맞춤법과 문장이 자연스러움
