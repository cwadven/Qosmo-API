-- NoSQL 학습 Questions 생성
WITH map_id AS (
  SELECT id FROM map_map WHERE name = '초보자도 따라해서 마스터 할 수 있는 NoSQL'
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
-- 기초 이론 그룹 문제
((SELECT id FROM map_id),
 'NoSQL의 개념과 특징',
 'NoSQL의 주요 특징 4가지를 설명하고, RDBMS와의 차이점을 서술하시오.',
 ARRAY['text'],
 'manual',
 true,
 'NoSQL의 주요 특징을 잘 이해하셨네요!',
 null,
 false, NOW(), NOW()),

((SELECT id FROM map_id),
 'NoSQL 데이터베이스 유형',
 '주요 NoSQL 데이터베이스 유형(Key-Value, Document, Column-Family, Graph)의 특징과 사용 사례를 설명하시오.',
 ARRAY['text'],
 'manual',
 true,
 '각 유형의 특징을 잘 파악하셨습니다!',
 null,
 false, NOW(), NOW()),

((SELECT id FROM map_id),
 'CAP 이론 이해하기',
 'CAP 이론의 각 요소를 설명하고, MongoDB, Cassandra, Redis가 CAP 중 어떤 특성을 선택했는지 설명하시오.',
 ARRAY['text'],
 'manual',
 true,
 'CAP 이론의 실제 적용 사례를 잘 이해하셨네요!',
 null,
 false, NOW(), NOW()),

-- MongoDB 그룹 문제
((SELECT id FROM map_id),
 'MongoDB CRUD 실습',
 '다음 요구사항에 맞는 MongoDB 쿼리를 작성하시오:
 1. 사용자 컬렉션 생성
 2. 새로운 사용자 문서 삽입
 3. 특정 조건으로 사용자 검색
 4. 사용자 정보 업데이트
 5. 특정 사용자 삭제',
 ARRAY['text'],
 'manual',
 true,
 'MongoDB의 기본 연산을 잘 수행하셨습니다!',
 null,
 false, NOW(), NOW()),

((SELECT id FROM map_id),
 'MongoDB 집계 파이프라인',
 '주어진 데이터셋에 대해 다음 집계 작업을 수행하는 파이프라인을 작성하시오:
 1. 카테고리별 제품 수 계산
 2. 가격 범위별 제품 분류
 3. 최상위 판매 제품 추출',
 ARRAY['text'],
 'manual',
 true,
 '집계 파이프라인을 효과적으로 구성하셨네요!',
 null,
 false, NOW(), NOW()),

((SELECT id FROM map_id),
 'MongoDB 인덱싱',
 'MongoDB의 인덱스 유형과 특징을 설명하고, 다음 시나리오에 적합한 인덱스 전략을 제시하시오:
 1. 복합 쿼리 최적화
 2. 정렬 성능 향상
 3. 지리공간 검색
 4. 텍스트 검색',
 ARRAY['text'],
 'manual',
 true,
 '인덱스 전략을 잘 수립하셨네요!',
 null,
 false, NOW(), NOW()),

((SELECT id FROM map_id),
 'MongoDB 복제',
 'MongoDB의 복제 세트 구성 방법과 장애 조치 프로세스를 설명하시오:
 1. Primary/Secondary 역할
 2. 선출 과정
 3. 복제 지연 모니터링
 4. 장애 복구 절차',
 ARRAY['text'],
 'manual',
 true,
 '복제 아키텍처를 잘 이해하셨네요!',
 null,
 false, NOW(), NOW()),

((SELECT id FROM map_id),
 'MongoDB 샤딩',
 'MongoDB 샤딩 클러스터 구성과 운영 방안을 설명하시오:
 1. 샤드 키 선정 기준
 2. 청크 분할 전략
 3. 밸런서 설정
 4. 라우팅 최적화',
 ARRAY['text'],
 'manual',
 true,
 '샤딩 구성 방안을 잘 이해하셨네요!',
 null,
 false, NOW(), NOW()),

-- Redis 그룹 문제
((SELECT id FROM map_id),
 'Redis 데이터 타입 활용',
 '다음 시나리오에 적합한 Redis 데이터 타입을 선택하고 명령어를 작성하시오:
 1. 실시간 랭킹 시스템
 2. 세션 관리
 3. 메시지 큐
 4. 캐시 시스템',
 ARRAY['text'],
 'manual',
 true,
 'Redis의 다양한 데이터 타입을 적절히 활용하셨습니다!',
 null,
 false, NOW(), NOW()),

((SELECT id FROM map_id),
 'Redis 캐시 설계',
 '다음 요구사항에 맞는 Redis 캐시 시스템을 설계하시오:
 1. 캐시 만료 정책
 2. 캐시 갱신 전략
 3. 캐시 키 설계
 4. 메모리 관리 방안',
 ARRAY['text'],
 'manual',
 true,
 '효율적인 캐시 시스템을 설계하셨네요!',
 null,
 false, NOW(), NOW()),

((SELECT id FROM map_id),
 'Redis 기초',
 'Redis의 주요 특징과 아키텍처를 설명하고, 다음 항목에 대해 서술하시오:
 1. 인메모리 동작 방식
 2. 단일 스레드 모델
 3. 이벤트 루프
 4. 네트워크 프로토콜',
 ARRAY['text'],
 'manual',
 true,
 'Redis의 기본 개념을 잘 이해하셨네요!',
 null,
 false, NOW(), NOW()),

((SELECT id FROM map_id),
 'Redis 데이터 타입',
 'Redis의 기본 데이터 타입별 특징과 활용 사례를 설명하시오:
 1. Strings
 2. Lists
 3. Sets
 4. Hashes
 5. Sorted Sets',
 ARRAY['text'],
 'manual',
 true,
 '데이터 타입별 특징을 잘 이해하셨네요!',
 null,
 false, NOW(), NOW()),

((SELECT id FROM map_id),
 'Redis 영속성',
 'Redis의 데이터 영속성 옵션을 설명하고 각각의 장단점을 비교하시오:
 1. RDB 스냅샷
 2. AOF 로그
 3. 하이브리드 방식
 4. 백업 전략',
 ARRAY['text'],
 'manual',
 true,
 '영속성 옵션을 잘 이해하셨네요!',
 null,
 false, NOW(), NOW()),

((SELECT id FROM map_id),
 'Redis Pub/Sub',
 'Redis의 Pub/Sub 시스템 구현 방법과 활용 사례를 설명하시오:
 1. 채널 구독/발행
 2. 패턴 매칭
 3. 메시지 전달 보장
 4. 실시간 처리',
 ARRAY['text'],
 'manual',
 true,
 'Pub/Sub 시스템을 잘 이해하셨네요!',
 null,
 false, NOW(), NOW()),

((SELECT id FROM map_id),
 'Redis 클러스터',
 'Redis 클러스터 구성과 운영 방안을 설명하시오:
 1. 마스터-슬레이브 구성
 2. 센티널 설정
 3. 클러스터 모드
 4. 장애 복구',
 ARRAY['text'],
 'manual',
 true,
 '클러스터 구성을 잘 이해하셨네요!',
 null,
 false, NOW(), NOW()),

-- Cassandra 그룹 문제
((SELECT id FROM map_id),
 'Cassandra 데이터 모델링',
 '주어진 요구사항에 맞는 Cassandra 데이터 모델을 설계하시오:
 1. 파티션 키 선정
 2. 클러스터링 키 구성
 3. 테이블 스키마 정의
 4. 쿼리 패턴 최적화',
 ARRAY['text'],
 'manual',
 true,
 'Cassandra에 최적화된 데이터 모델을 설계하셨습니다!',
 null,
 false, NOW(), NOW()),

((SELECT id FROM map_id),
 'Cassandra 클러스터 설계',
 '다음 시나리오에 대한 Cassandra 클러스터 구성 방안을 제시하시오:
 1. 복제 전략
 2. 일관성 수준 설정
 3. 노드 구성 방안
 4. 장애 대응 전략',
 ARRAY['text'],
 'manual',
 true,
 '안정적인 클러스터 구성 방안을 제시하셨네요!',
 null,
 false, NOW(), NOW()),

((SELECT id FROM map_id),
 'Cassandra 기초',
 'Cassandra의 주요 특징과 아키텍처를 설명하시오:
 1. 분산 시스템 구조
 2. 링 아키텍처
 3. 피어-투-피어 통신
 4. 데이터 분산 방식',
 ARRAY['text'],
 'manual',
 true,
 'Cassandra의 기본 구조를 잘 이해하셨네요!',
 null,
 false, NOW(), NOW()),

((SELECT id FROM map_id),
 'Cassandra CQL',
 'Cassandra Query Language의 특징과 사용법을 설명하시오:
 1. CQL과 SQL의 차이점
 2. 테이블 생성과 관리
 3. CRUD 연산
 4. 인덱스 활용',
 ARRAY['text'],
 'manual',
 true,
 'CQL의 특징을 잘 이해하셨네요!',
 null,
 false, NOW(), NOW()),

((SELECT id FROM map_id),
 'Cassandra 아키텍처',
 'Cassandra의 내부 아키텍처와 동작 방식을 설명하시오:
 1. 데이터 저장 구조
 2. 커밋 로그와 멤테이블
 3. 컴팩션 전략
 4. 가십 프로토콜',
 ARRAY['text'],
 'manual',
 true,
 '아키텍처의 동작 방식을 잘 이해하셨네요!',
 null,
 false, NOW(), NOW()),

((SELECT id FROM map_id),
 'Cassandra 일관성',
 'Cassandra의 일관성 모델과 튜닝 방법을 설명하시오:
 1. 일관성 수준 설정
 2. 읽기/쓰기 쿼럼
 3. 힌트 핸드오프
 4. 읽기 복구',
 ARRAY['text'],
 'manual',
 true,
 '일관성 관리 방법을 잘 이해하셨네요!',
 null,
 false, NOW(), NOW()),

-- 실전/응용 그룹 문제
((SELECT id FROM map_id),
 '마이그레이션 전략',
 'RDBMS에서 NoSQL로의 마이그레이션 계획을 수립하시오:
 1. 데이터 모델 변환 전략
 2. 단계별 마이그레이션 계획
 3. 검증 방안
 4. 롤백 계획',
 ARRAY['text'],
 'manual',
 true,
 '체계적인 마이그레이션 계획을 수립하셨습니다!',
 null,
 false, NOW(), NOW()),

((SELECT id FROM map_id),
 '성능 최적화',
 '다음 성능 이슈에 대한 해결 방안을 제시하시오:
 1. 쿼리 성능 개선
 2. 인덱스 최적화
 3. 메모리 사용량 조정
 4. 네트워크 지연 감소',
 ARRAY['text'],
 'manual',
 true,
 '효과적인 성능 최적화 방안을 제시하셨네요!',
 null,
 false, NOW(), NOW()),

-- 추가되어야 할 문제들
((SELECT id FROM map_id),
 'ACID와 BASE',
 'ACID와 BASE 속성을 각각 설명하고, NoSQL에서 BASE를 선택하는 이유를 설명하시오.',
 ARRAY['text'],
 'manual',
 true,
 'ACID와 BASE의 차이점을 잘 이해하셨네요!',
 null,
 false, NOW(), NOW()),

((SELECT id FROM map_id),
 '확장성 패턴',
 'NoSQL의 수평적 확장과 수직적 확장의 차이점을 설명하고, 각각의 장단점을 서술하시오.',
 ARRAY['text'],
 'manual',
 true,
 '확장성 패턴의 특징을 잘 이해하셨네요!',
 null,
 false, NOW(), NOW()),

((SELECT id FROM map_id),
 'MongoDB 기초',
 'MongoDB의 기본 구성요소(데이터베이스, 컬렉션, 문서)를 설명하고, JSON 문서 기반 저장 방식의 장점을 서술하시오.',
 ARRAY['text'],
 'manual',
 true,
 'MongoDB의 기본 개념을 잘 이해하셨네요!',
 null,
 false, NOW(), NOW()),

((SELECT id FROM map_id),
 'NoSQL 활용 사례',
 '다양한 NoSQL 데이터베이스의 실제 활용 사례를 분석하시오:
 1. 소셜 미디어 플랫폼
 2. IoT 데이터 처리
 3. 실시간 분석 시스템
 4. 게임 서버',
 ARRAY['text'],
 'manual',
 true,
 '활용 사례를 잘 분석하셨네요!',
 null,
 false, NOW(), NOW()),

((SELECT id FROM map_id),
 'NoSQL 모니터링',
 'NoSQL 데이터베이스의 모니터링 전략을 수립하시오:
 1. 성능 메트릭 수집
 2. 알림 설정
 3. 로그 분석
 4. 리소스 모니터링',
 ARRAY['text'],
 'manual',
 true,
 '모니터링 전략을 잘 수립하셨네요!',
 null,
 false, NOW(), NOW()),

((SELECT id FROM map_id),
 'NoSQL 보안',
 'NoSQL 데이터베이스의 보안 설정 방안을 제시하시오:
 1. 인증/인가 설정
 2. 네트워크 보안
 3. 암호화 전략
 4. 감사 로깅',
 ARRAY['text'],
 'manual',
 true,
 '보안 설정 방안을 잘 제시하셨네요!',
 null,
 false, NOW(), NOW()),

((SELECT id FROM map_id),
 '백업과 복구',
 'NoSQL 데이터베이스의 백업 및 복구 전략을 수립하시오:
 1. 백업 방식 선택
 2. 스케줄링
 3. 복구 절차
 4. 정합성 검증',
 ARRAY['text'],
 'manual',
 true,
 '백업/복구 전략을 잘 수립하셨네요!',
 null,
 false, NOW(), NOW()); 