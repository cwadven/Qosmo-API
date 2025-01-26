#### 1. 파일 작성 순서 관련
- 체크리스트(.check.md) 파일을 먼저 작성한 후 SQL 파일을 작성해야 함
- 불필요하게 스스로 생각해서 추가적인 체크리스트를 만들지 말고 무조건 문서 안에 있는 체크리스트만 사용해야 함
- 체크리스트를 기준으로 SQL 파일의 완성도를 검증해야 함
- 파일 작성 전에 관련된 모든 규칙 문서를 처음부터 끝까지 꼼꼼히 읽어야 함
- SQL 파일은 '00_map.sql' -> '01_nodes.sql' -> '02_node_complete_rules.sql' -> '03_questions.sql' -> '04_self_arrows.sql' -> '05_arrows.sql' 순서로 작성해야 함
- 참고해야하는 대응되는 문서는
  -'00_map.sql' -> '1_CREATE_RULE_MAP.md'
  -'01_nodes.sql' -> '2_CREATE_RULE_NODE.md'
  -'02_node_complete_rules.sql' -> '3_CREATE_RULE_NODE_COMPLETE_RULE.md'
  -'03_questions.sql' -> '4_CREATE_RULE_QUESTION.md'
  -'04_self_arrows.sql' -> '5_CREATE_RULE_SELF_ARROW.md'
  -'05_arrows.sql' -> '6_CREATE_RULE_ARROW.md'

#### 2. SQL 작성 관련
- WITH 구문에는 필요한 테이블만 포함해야 함 (불필요한 테이블 참조 금지)
- 각 필드의 용도를 정확히 이해하고 사용해야 함 (예: question_id가 필요한 경우와 null이어야 하는 경우 구분)
- 모든 SQL 문은 세미콜론(;)으로 종료해야 함
- 참조하는 필드가 올바른지 확인해야 함 (예: node_complete_rule_id가 start_node의 것인지 end_node의 것인지)

#### 3. 화살표 생성 규칙 관련
- self-arrow와 node 간 화살표의 차이를 명확히 구분해야 함
  - self-arrow: 노드 자신을 가리키며, 완료 규칙과 검증 질문을 연결
  - node 간 화살표: 학습 순서를 나타내며, 시작 노드의 완료 규칙만 연결하고 question_id는 null
- 그룹 내 연결과 그룹 간 연결을 명확히 구분해야 함
- node_complete_rule_id 참조 규칙을 정확히 따라야 함
  - self-arrow: 자기 자신의 완료 규칙
  - node 간 화살표: 도착 노드(end_node)의 완료 규칙

#### 4. 파일 구조 관련
- 파일명 규칙을 정확히 따라야 함
- 각 파일의 목적과 역할을 명확히 이해하고 작성해야 함
- 체크리스트와 SQL 파일은 쌍으로 관리되어야 함
- 파일 간의 의존성과 순서를 이해하고 작성해야 함

#### 5. 코드 가독성 관련
- 그룹 구분을 위한 주석을 명확히 작성해야 함
- 일관된 들여쓰기를 사용해야 함
- SQL 문의 각 부분을 논리적으로 구분하여 작성해야 함
- 주석은 해당 섹션의 목적을 명확히 설명해야 함

#### 6. 검증 관련
- 작성 완료 후 체크리스트로 철저히 검증해야 함
- 다른 파일의 규칙이나 내용과 충돌하지 않는지 확인해야 함
- 특히 node_complete_rule_id, question_id와 같은 참조 필드의 정확성을 재확인해야 함
- 순환 참조가 없는지 확인해야 함