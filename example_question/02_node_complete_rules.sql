-- NodeCompleteRule 생성
INSERT INTO map_nodecompleterule (map_id, node_id, name, is_deleted, created_at, updated_at) VALUES
-- Java 기초
(2, (SELECT id FROM map_node WHERE map_id = 2 AND name = 'Java 설치와 환경설정'), 
 'Java 개발 환경 구축 완료', false, NOW(), NOW()),

(2, (SELECT id FROM map_node WHERE map_id = 2 AND name = 'Java 기초 문법'), 
 'Java 기초 문법 학습 완료', false, NOW(), NOW()),

(2, (SELECT id FROM map_node WHERE map_id = 2 AND name = '객체지향 기초'), 
 '객체지향 프로그래밍 이해 완료', false, NOW(), NOW()),

-- Java 심화
(2, (SELECT id FROM map_node WHERE map_id = 2 AND name = '컬렉션 프레임워크'), 
 '컬렉션 프레임워크 학습 완료', false, NOW(), NOW()),

(2, (SELECT id FROM map_node WHERE map_id = 2 AND name = '예외처리'), 
 '예외처리 학습 완료', false, NOW(), NOW()),

(2, (SELECT id FROM map_node WHERE map_id = 2 AND name = '스트림 API'), 
 '스트림 API 학습 완료', false, NOW(), NOW()),

-- 백엔드 기초
(2, (SELECT id FROM map_node WHERE map_id = 2 AND name = 'SQL 기초'), 
 'SQL 기초 학습 완료', false, NOW(), NOW()),

(2, (SELECT id FROM map_node WHERE map_id = 2 AND name = 'JDBC'), 
 'JDBC 프로그래밍 완료', false, NOW(), NOW()),

(2, (SELECT id FROM map_node WHERE map_id = 2 AND name = '서블릿/JSP'), 
 '서블릿/JSP 학습 완료', false, NOW(), NOW()),

-- Spring 프레임워크
(2, (SELECT id FROM map_node WHERE map_id = 2 AND name = 'Spring Core'), 
 'Spring Core 학습 완료', false, NOW(), NOW()),

(2, (SELECT id FROM map_node WHERE map_id = 2 AND name = 'Spring MVC'), 
 'Spring MVC 학습 완료', false, NOW(), NOW()),

(2, (SELECT id FROM map_node WHERE map_id = 2 AND name = 'Spring Boot'), 
 'Spring Boot 학습 완료', false, NOW(), NOW()),

-- 백엔드 심화
(2, (SELECT id FROM map_node WHERE map_id = 2 AND name = 'JPA/Hibernate'), 
 'JPA/Hibernate 학습 완료', false, NOW(), NOW()),

(2, (SELECT id FROM map_node WHERE map_id = 2 AND name = 'Spring Security'), 
 'Spring Security 학습 완료', false, NOW(), NOW()),

(2, (SELECT id FROM map_node WHERE map_id = 2 AND name = 'REST API'), 
 'REST API 개발 완료', false, NOW(), NOW()),

-- 실전/운영
(2, (SELECT id FROM map_node WHERE map_id = 2 AND name = '테스트 코드'), 
 '테스트 코드 작성 완료', false, NOW(), NOW()),

(2, (SELECT id FROM map_node WHERE map_id = 2 AND name = '성능 최적화'), 
 '성능 최적화 완료', false, NOW(), NOW()),

(2, (SELECT id FROM map_node WHERE map_id = 2 AND name = '배포와 운영'), 
 '배포 환경 구축 완료', false, NOW(), NOW()),

-- Spring Boot 진입을 위한 추가 Node들의 CompleteRule
(2, (SELECT id FROM map_node WHERE map_id = 2 AND name = 'JPA 기초'), 
 'JPA 기초 개념 학습 완료', false, NOW(), NOW()),

(2, (SELECT id FROM map_node WHERE map_id = 2 AND name = 'REST API 기초'), 
 'REST API 기초 이해 완료', false, NOW(), NOW()),

(2, (SELECT id FROM map_node WHERE map_id = 2 AND name = 'Spring Data JPA'), 
 'Spring Data JPA 학습 완료', false, NOW(), NOW()),

(2, (SELECT id FROM map_node WHERE map_id = 2 AND name = 'API 문서화'), 
 'API 문서화 도구 활용 완료', false, NOW(), NOW()); 