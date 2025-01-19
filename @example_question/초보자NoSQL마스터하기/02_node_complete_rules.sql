-- NoSQL 학습 Node Complete Rules 생성
WITH map_id AS (
  SELECT id FROM map_map WHERE name = '초보자도 따라해서 마스터 할 수 있는 NoSQL'
)
INSERT INTO map_nodecompleterule (map_id, node_id, name, is_deleted, created_at, updated_at) VALUES
-- 기초 이론 그룹
((SELECT id FROM map_id), (SELECT id FROM map_node WHERE map_id = (SELECT id FROM map_id) AND name = 'nosql_intro'), 'NoSQL 소개 학습', false, NOW(), NOW()),
((SELECT id FROM map_id), (SELECT id FROM map_node WHERE map_id = (SELECT id FROM map_id) AND name = 'nosql_types'), 'NoSQL 유형 이해', false, NOW(), NOW()),
((SELECT id FROM map_id), (SELECT id FROM map_node WHERE map_id = (SELECT id FROM map_id) AND name = 'cap_theorem'), 'CAP 이론 학습', false, NOW(), NOW()),
((SELECT id FROM map_id), (SELECT id FROM map_node WHERE map_id = (SELECT id FROM map_id) AND name = 'data_modeling'), '데이터 모델링 실습', false, NOW(), NOW()),
((SELECT id FROM map_id), (SELECT id FROM map_node WHERE map_id = (SELECT id FROM map_id) AND name = 'acid_base'), 'ACID/BASE 이해', false, NOW(), NOW()),
((SELECT id FROM map_id), (SELECT id FROM map_node WHERE map_id = (SELECT id FROM map_id) AND name = 'scaling_patterns'), '확장성 패턴 학습', false, NOW(), NOW()),

-- MongoDB 그룹
((SELECT id FROM map_id), (SELECT id FROM map_node WHERE map_id = (SELECT id FROM map_id) AND name = 'mongo_basics'), 'MongoDB 기초 학습', false, NOW(), NOW()),
((SELECT id FROM map_id), (SELECT id FROM map_node WHERE map_id = (SELECT id FROM map_id) AND name = 'mongo_crud'), 'CRUD 연산 실습', false, NOW(), NOW()),
((SELECT id FROM map_id), (SELECT id FROM map_node WHERE map_id = (SELECT id FROM map_id) AND name = 'mongo_aggregation'), '집계 프레임워크 실습', false, NOW(), NOW()),
((SELECT id FROM map_id), (SELECT id FROM map_node WHERE map_id = (SELECT id FROM map_id) AND name = 'mongo_index'), '인덱스 설계 실습', false, NOW(), NOW()),
((SELECT id FROM map_id), (SELECT id FROM map_node WHERE map_id = (SELECT id FROM map_id) AND name = 'mongo_replication'), '복제 설정 실습', false, NOW(), NOW()),
((SELECT id FROM map_id), (SELECT id FROM map_node WHERE map_id = (SELECT id FROM map_id) AND name = 'mongo_sharding'), '샤딩 구성 실습', false, NOW(), NOW()),

-- Redis 그룹
((SELECT id FROM map_id), (SELECT id FROM map_node WHERE map_id = (SELECT id FROM map_id) AND name = 'redis_basics'), 'Redis 기초 학습', false, NOW(), NOW()),
((SELECT id FROM map_id), (SELECT id FROM map_node WHERE map_id = (SELECT id FROM map_id) AND name = 'redis_datatype'), '데이터 타입 실습', false, NOW(), NOW()),
((SELECT id FROM map_id), (SELECT id FROM map_node WHERE map_id = (SELECT id FROM map_id) AND name = 'redis_persistence'), '영속성 설정 실습', false, NOW(), NOW()),
((SELECT id FROM map_id), (SELECT id FROM map_node WHERE map_id = (SELECT id FROM map_id) AND name = 'redis_pubsub'), 'Pub/Sub 실습', false, NOW(), NOW()),
((SELECT id FROM map_id), (SELECT id FROM map_node WHERE map_id = (SELECT id FROM map_id) AND name = 'redis_cache'), '캐시 서버 구성', false, NOW(), NOW()),
((SELECT id FROM map_id), (SELECT id FROM map_node WHERE map_id = (SELECT id FROM map_id) AND name = 'redis_cluster'), '클러스터 구성 실습', false, NOW(), NOW()),

-- Cassandra 그룹
((SELECT id FROM map_id), (SELECT id FROM map_node WHERE map_id = (SELECT id FROM map_id) AND name = 'cassandra_basics'), 'Cassandra 기초 학습', false, NOW(), NOW()),
((SELECT id FROM map_id), (SELECT id FROM map_node WHERE map_id = (SELECT id FROM map_id) AND name = 'cassandra_model'), '데이터 모델링 실습', false, NOW(), NOW()),
((SELECT id FROM map_id), (SELECT id FROM map_node WHERE map_id = (SELECT id FROM map_id) AND name = 'cassandra_cql'), 'CQL 실습', false, NOW(), NOW()),
((SELECT id FROM map_id), (SELECT id FROM map_node WHERE map_id = (SELECT id FROM map_id) AND name = 'cassandra_arch'), '아키텍처 이해', false, NOW(), NOW()),
((SELECT id FROM map_id), (SELECT id FROM map_node WHERE map_id = (SELECT id FROM map_id) AND name = 'cassandra_consist'), '일관성 튜닝 실습', false, NOW(), NOW()),
((SELECT id FROM map_id), (SELECT id FROM map_node WHERE map_id = (SELECT id FROM map_id) AND name = 'cassandra_perf'), '성능 최적화 실습', false, NOW(), NOW()),

-- 실전/응용 그룹
((SELECT id FROM map_id), (SELECT id FROM map_node WHERE map_id = (SELECT id FROM map_id) AND name = 'usecase_analysis'), '활용 사례 학습', false, NOW(), NOW()),
((SELECT id FROM map_id), (SELECT id FROM map_node WHERE map_id = (SELECT id FROM map_id) AND name = 'migration'), '마이그레이션 실습', false, NOW(), NOW()),
((SELECT id FROM map_id), (SELECT id FROM map_node WHERE map_id = (SELECT id FROM map_id) AND name = 'monitoring'), '모니터링 실습', false, NOW(), NOW()),
((SELECT id FROM map_id), (SELECT id FROM map_node WHERE map_id = (SELECT id FROM map_id) AND name = 'security'), '보안 설정 실습', false, NOW(), NOW()),
((SELECT id FROM map_id), (SELECT id FROM map_node WHERE map_id = (SELECT id FROM map_id) AND name = 'backup'), '백업/복구 실습', false, NOW(), NOW()),
((SELECT id FROM map_id), (SELECT id FROM map_node WHERE map_id = (SELECT id FROM map_id) AND name = 'best_practice'), '모범 사례 학습', false, NOW(), NOW()); 