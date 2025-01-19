-- NoSQL 학습 노드 생성
WITH map_id AS (
  SELECT id FROM map_map WHERE name = '초보자도 따라해서 마스터 할 수 있는 NoSQL'
)
INSERT INTO map_node (map_id, name, title, description, position_x, position_y, width, height, is_active, is_deleted, created_at, updated_at) VALUES
-- 기초 이론 그룹 (y=100)
((SELECT id FROM map_id), 'nosql_intro', 'NoSQL 소개', 'NoSQL의 기본 개념과 등장 배경에 대해 학습합니다.', 100, 100, 150, 100, true, false, NOW(), NOW()),
((SELECT id FROM map_id), 'nosql_types', 'NoSQL 유형', '다양한 NoSQL 데이터베이스의 유형과 특징을 이해합니다.', 400, 100, 150, 100, true, false, NOW(), NOW()),
((SELECT id FROM map_id), 'cap_theorem', 'CAP 이론', 'CAP 이론과 NoSQL의 관계에 대해 학습합니다.', 700, 100, 150, 100, true, false, NOW(), NOW()),
((SELECT id FROM map_id), 'data_modeling', 'NoSQL 데이터 모델링', 'NoSQL에서의 효과적인 데이터 모델링 방법을 학습합니다.', 1000, 100, 150, 100, true, false, NOW(), NOW()),
((SELECT id FROM map_id), 'acid_base', 'ACID와 BASE', 'ACID와 BASE 속성의 차이점과 특징을 이해합니다.', 1300, 100, 150, 100, true, false, NOW(), NOW()),
((SELECT id FROM map_id), 'scaling_patterns', '확장성 패턴', 'NoSQL의 수평적/수직적 확장 패턴을 학습합니다.', 1600, 100, 150, 100, true, false, NOW(), NOW()),

-- MongoDB 그룹 (y=400)
((SELECT id FROM map_id), 'mongo_basics', 'MongoDB 기초', 'MongoDB의 기본 개념과 특징을 학습합니다.', 100, 400, 150, 100, true, false, NOW(), NOW()),
((SELECT id FROM map_id), 'mongo_crud', 'MongoDB CRUD', '기본적인 CRUD 연산을 실습합니다.', 400, 400, 150, 100, true, false, NOW(), NOW()),
((SELECT id FROM map_id), 'mongo_aggregation', '집계 프레임워크', '데이터 집계와 분석 방법을 학습합니다.', 700, 400, 150, 100, true, false, NOW(), NOW()),
((SELECT id FROM map_id), 'mongo_index', '인덱싱', '효율적인 쿼리를 위한 인덱스 설계를 배웁니다.', 1000, 400, 150, 100, true, false, NOW(), NOW()),
((SELECT id FROM map_id), 'mongo_replication', '복제', '고가용성을 위한 복제 설정을 학습합니다.', 1300, 400, 150, 100, true, false, NOW(), NOW()),
((SELECT id FROM map_id), 'mongo_sharding', '샤딩', '수평적 확장을 위한 샤딩 구성을 배웁니다.', 1600, 400, 150, 100, true, false, NOW(), NOW()),

-- Redis 그룹 (y=700)
((SELECT id FROM map_id), 'redis_basics', 'Redis 기초', 'Redis의 기본 개념과 특징을 학습합니다.', 100, 700, 150, 100, true, false, NOW(), NOW()),
((SELECT id FROM map_id), 'redis_datatype', '데이터 타입', 'Redis의 다양한 데이터 타입을 실습합니다.', 400, 700, 150, 100, true, false, NOW(), NOW()),
((SELECT id FROM map_id), 'redis_persistence', '영속성', '데이터 지속성 보장 방법을 학습합니다.', 700, 700, 150, 100, true, false, NOW(), NOW()),
((SELECT id FROM map_id), 'redis_pubsub', 'Pub/Sub', '메시지 브로커로서의 활용법을 배웁니다.', 1000, 700, 150, 100, true, false, NOW(), NOW()),
((SELECT id FROM map_id), 'redis_cache', '캐시', '캐시 서버로서의 활용 방법을 학습합니다.', 1300, 700, 150, 100, true, false, NOW(), NOW()),
((SELECT id FROM map_id), 'redis_cluster', '클러스터', '분산 시스템 구성 방법을 배웁니다.', 1600, 700, 150, 100, true, false, NOW(), NOW()),

-- Cassandra 그룹 (y=1000)
((SELECT id FROM map_id), 'cassandra_basics', 'Cassandra 기초', 'Cassandra의 기본 개념과 특징을 학습합니다.', 100, 1000, 150, 100, true, false, NOW(), NOW()),
((SELECT id FROM map_id), 'cassandra_model', '데이터 모델링', 'Cassandra 특화 데이터 모델링을 배웁니다.', 400, 1000, 150, 100, true, false, NOW(), NOW()),
((SELECT id FROM map_id), 'cassandra_cql', 'CQL', 'Cassandra Query Language를 실습합니다.', 700, 1000, 150, 100, true, false, NOW(), NOW()),
((SELECT id FROM map_id), 'cassandra_arch', '아키텍처', '분산 아키텍처의 동작 원리를 이해합니다.', 1000, 1000, 150, 100, true, false, NOW(), NOW()),
((SELECT id FROM map_id), 'cassandra_consist', '일관성', '일관성 수준과 튜닝 방법을 학습합니다.', 1300, 1000, 150, 100, true, false, NOW(), NOW()),
((SELECT id FROM map_id), 'cassandra_perf', '성능 최적화', '성능 튜닝과 모니터링을 배웁니다.', 1600, 1000, 150, 100, true, false, NOW(), NOW()),

-- 실전/응용 그룹 (y=1300)
((SELECT id FROM map_id), 'usecase_analysis', '활용 사례 분석', '다양한 NoSQL 활용 사례를 학습합니다.', 100, 1300, 150, 100, true, false, NOW(), NOW()),
((SELECT id FROM map_id), 'migration', '마이그레이션', 'RDBMS에서 NoSQL로의 전환을 배웁니다.', 400, 1300, 150, 100, true, false, NOW(), NOW()),
((SELECT id FROM map_id), 'monitoring', '모니터링', '운영 모니터링과 문제 해결을 학습합니다.', 700, 1300, 150, 100, true, false, NOW(), NOW()),
((SELECT id FROM map_id), 'security', '보안', '보안 설정과 취약점 대응을 배웁니다.', 1000, 1300, 150, 100, true, false, NOW(), NOW()),
((SELECT id FROM map_id), 'backup', '백업과 복구', '데이터 백업과 복구 전략을 학습합니다.', 1300, 1300, 150, 100, true, false, NOW(), NOW()),
((SELECT id FROM map_id), 'best_practice', '모범 사례', '실전 운영의 모범 사례를 배웁니다.', 1600, 1300, 150, 100, true, false, NOW(), NOW()); 