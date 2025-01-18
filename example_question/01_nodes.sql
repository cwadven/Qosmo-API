-- Java 백엔드 개발자 과정의 Nodes 생성
INSERT INTO map_node (map_id, name, title, description, position_x, position_y, width, height, is_active, is_deleted, created_at, updated_at) VALUES
-- Java 기초
(2, 'Java 설치와 환경설정', 'JDK 설치 및 개발환경 구축', 'Java Development Kit 설치와 IDE 설정 방법을 학습합니다.', 100, 100, 100, 100, true, false, NOW(), NOW()),
(2, 'Java 기초 문법', 'Java 기본 문법 마스터', '변수, 데이터타입, 연산자, 제어문 등 기초 문법을 배웁니다.', 300, 100, 100, 100, true, false, NOW(), NOW()),
(2, '객체지향 기초', 'OOP의 기본 개념', '클래스, 객체, 상속, 다형성 등 객체지향의 핵심 개념을 학습합니다.', 500, 100, 100, 100, true, false, NOW(), NOW()),

-- Java 심화
(2, '컬렉션 프레임워크', '자료구조와 컬렉션', 'List, Set, Map 등 Java 컬렉션 프레임워크를 마스터합니다.', 100, 200, 100, 100, true, false, NOW(), NOW()),
(2, '예외처리', '예외처리와 디버깅', '다양한 예외 상황 처리와 효과적인 디버깅 방법을 배웁니다.', 300, 200, 100, 100, true, false, NOW(), NOW()),
(2, '스트림 API', '함수형 프로그래밍', '람다식과 스트림 API를 활용한 함수형 프로그래밍을 학습합니다.', 500, 200, 100, 100, true, false, NOW(), NOW()),

-- 백엔드 기초
(2, 'SQL 기초', '데이터베이스와 SQL', 'RDBMS 개념과 SQL 쿼리 작성법을 배웁니다.', 100, 300, 100, 100, true, false, NOW(), NOW()),
(2, 'JDBC', 'JDBC 프로그래밍', 'Java와 데이터베이스 연동 방법을 학습합니다.', 300, 300, 100, 100, true, false, NOW(), NOW()),
(2, '서블릿/JSP', '웹 프로그래밍 기초', '서블릿과 JSP를 이용한 웹 애플리케이션 개발을 배웁니다.', 500, 300, 100, 100, true, false, NOW(), NOW()),

-- Spring 프레임워크 기초
(2, 'Spring Core', 'Spring 핵심 개념', 'IoC, DI 등 Spring 프레임워크의 핵심 개념을 학습합니다.', 100, 400, 100, 100, true, false, NOW(), NOW()),
(2, 'Spring MVC', 'Spring MVC 패턴', 'Spring MVC 구조와 웹 애플리케이션 개발 방법을 배웁니다.', 300, 400, 100, 100, true, false, NOW(), NOW()),

-- Spring Boot 진입 경로 1 (JPA)
(2, 'JPA 기초', 'JPA 기본 개념 이해', 'JPA의 기본 개념과 Entity 매핑을 학습합니다.', 100, 500, 100, 100, true, false, NOW(), NOW()),
(2, 'Spring Data JPA', 'Spring Data JPA 활용', 'Spring Data JPA를 사용한 데이터 접근 계층을 구현합니다.', 100, 600, 100, 100, true, false, NOW(), NOW()),

-- Spring Boot 진입 경로 2 (REST)
(2, 'REST API 기초', 'REST 아키텍처의 이해', 'REST 아키텍처 스타일과 API 설계 원칙을 학습합니다.', 500, 500, 100, 100, true, false, NOW(), NOW()),
(2, 'API 문서화', 'Swagger/OpenAPI 활용', 'API 문서 자동화 도구 사용법을 학습합니다.', 500, 600, 100, 100, true, false, NOW(), NOW()),

-- Spring Boot와 심화 과정
(2, 'Spring Boot', 'Spring Boot 실전', 'Spring Boot를 이용한 실전 애플리케이션 개발을 학습합니다.', 300, 700, 100, 100, true, false, NOW(), NOW()),
(2, 'JPA/Hibernate', 'ORM과 JPA', 'JPA를 이용한 객체-관계 매핑과 데이터 처리를 배웁니다.', 100, 800, 100, 100, true, false, NOW(), NOW()),
(2, 'Spring Security', '보안과 인증', '인증/인가 처리와 보안 기능 구현 방법을 학습합니다.', 300, 800, 100, 100, true, false, NOW(), NOW()),
(2, 'REST API', 'RESTful 서비스 개발', 'REST API 설계와 개발 방법을 배웁니다.', 500, 800, 100, 100, true, false, NOW(), NOW()),

-- 실전/운영
(2, '테스트 코드', '단위/통합 테스트', 'JUnit을 이용한 테스트 코드 작성법을 학습합니다.', 200, 900, 100, 100, true, false, NOW(), NOW()),
(2, '성능 최적화', '성능 튜닝과 모니터링', '애플리케이션 성능 최적화와 모니터링 방법을 배웁니다.', 400, 900, 100, 100, true, false, NOW(), NOW()),
(2, '배포와 운영', 'DevOps 기초', 'CI/CD, 도커, AWS 등 운영 환경 구축 방법을 학습합니다.', 300, 1000, 100, 100, true, false, NOW(), NOW()); 