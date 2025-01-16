-- QuestionAnswers 생성
INSERT INTO question_questionanswer (
    map_id,
    question_id,
    answer,
    description,
    is_deleted,
    created_at,
    updated_at
) VALUES
-- Java 기초
(2, 
 (SELECT id FROM question_question WHERE map_id = 2 AND title = 'Java 개발 환경 구축하기'), 
 '1. JDK 설치 완료\n2. IDE 설정 완료\n3. Hello World 실행 성공',
 'Java 개발 환경이 정상적으로 구축되었습니다. 콘솔에서 Hello World가 정상적으로 출력되어야 합니다.',
 false, NOW(), NOW()),

(2,
 (SELECT id FROM question_question WHERE map_id = 2 AND title = 'Java 기초 문법 실습'),
 'System.out.println("Hello, Java Programming!");',
 '정확한 문자열을 출력하는 Java 명령문입니다.',
 false, NOW(), NOW()),

(2,
 (SELECT id FROM question_question WHERE map_id = 2 AND title = '객체지향 프로그래밍 실습'),
 'public class Animal {\n    public void sound() {\n        System.out.println("Animal sound");\n    }\n}\n\npublic class Dog extends Animal {\n    @Override\n    public void sound() {\n        System.out.println("Woof");\n    }\n}',
 '상속과 메서드 오버라이딩을 사용한 객체지향 프로그래밍의 예시입니다.',
 false, NOW(), NOW()),

-- Java 심화
(2,
 (SELECT id FROM question_question WHERE map_id = 2 AND title = '컬렉션 프레임워크 활용'),
 'List<String> names = new ArrayList<>();\nnames.add("John");\nboolean exists = names.contains("John");\nnames.remove("John");',
 'ArrayList를 사용한 기본적인 CRUD 작업의 예시입니다.',
 false, NOW(), NOW()),

(2,
 (SELECT id FROM question_question WHERE map_id = 2 AND title = '예외 처리 구현하기'),
 'try {\n    FileReader fr = new FileReader("file.txt");\n    // 파일 처리 로직\n} catch (FileNotFoundException e) {\n    System.err.println("파일을 찾을 수 없습니다.");\n} catch (IOException e) {\n    System.err.println("입출력 오류가 발생했습니다.");\n}',
 '파일 처리 시 발생할 수 있는 주요 예외들을 처리하는 예시 코드입니다.',
 false, NOW(), NOW()),

(2,
 (SELECT id FROM question_question WHERE map_id = 2 AND title = '스트림 API 실습'),
 'List<Integer> numbers = Arrays.asList(5, 2, 8, 1, 9, 4);\nList<Integer> result = numbers.stream()\n    .filter(n -> n % 2 == 0)\n    .sorted()\n    .collect(Collectors.toList());',
 '스트림 API를 사용하여 짝수를 필터링하고 정렬하는 예시입니다.',
 false, NOW(), NOW()),

-- 백엔드 기초
(2,
 (SELECT id FROM question_question WHERE map_id = 2 AND title = 'SQL 기초 실습'),
 'CREATE TABLE users (\n    id INT PRIMARY KEY,\n    name VARCHAR(50),\n    email VARCHAR(100)\n);\n\nINSERT INTO users VALUES (1, "John", "john@example.com");\n\nSELECT * FROM users WHERE id = 1;',
 '기본적인 SQL DDL과 DML 문의 예시입니다.',
 false, NOW(), NOW()),

(2,
 (SELECT id FROM question_question WHERE map_id = 2 AND title = 'JDBC 프로그래밍'),
 'Connection conn = DriverManager.getConnection(url, user, password);\nPreparedStatement pstmt = conn.prepareStatement("INSERT INTO users VALUES (?, ?, ?)");\npstmt.setInt(1, 1);\npstmt.setString(2, "John");\npstmt.setString(3, "john@example.com");\npstmt.executeUpdate();',
 'JDBC를 사용한 데이터베이스 연결과 데이터 삽입 예시입니다.',
 false, NOW(), NOW()),

-- Spring 프레임워크
(2,
 (SELECT id FROM question_question WHERE map_id = 2 AND title = 'Spring Core 실습'),
 '@Service\npublic class BookServiceImpl implements BookService {\n    @Autowired\n    private BookRepository bookRepository;\n    \n    @Override\n    public Book findById(Long id) {\n        return bookRepository.findById(id);\n    }\n}',
 'Spring DI를 사용한 서비스 계층 구현 예시입니다.',
 false, NOW(), NOW()),

(2,
 (SELECT id FROM question_question WHERE map_id = 2 AND title = 'Spring MVC 구현'),
 '@Controller\n@RequestMapping("/books")\npublic class BookController {\n    @Autowired\n    private BookService bookService;\n    \n    @GetMapping\n    public String list(Model model) {\n        model.addAttribute("books", bookService.findAll());\n        return "books/list";\n    }\n}',
 'Spring MVC 컨트롤러 구현 예시입니다.',
 false, NOW(), NOW()),

-- 백엔드 심화
(2,
 (SELECT id FROM question_question WHERE map_id = 2 AND title = 'JPA/Hibernate 실습'),
 '@Entity\npublic class Book {\n    @Id @GeneratedValue\n    private Long id;\n    \n    @ManyToMany\n    @JoinTable(name = "book_author")\n    private Set<Author> authors;\n}',
 'JPA 엔티티와 다대다 관계 매핑 예시입니다.',
 false, NOW(), NOW()),

(2,
 (SELECT id FROM question_question WHERE map_id = 2 AND title = 'Spring Security 구현'),
 '@Configuration\n@EnableWebSecurity\npublic class SecurityConfig extends WebSecurityConfigurerAdapter {\n    @Override\n    protected void configure(HttpSecurity http) throws Exception {\n        http.authorizeRequests()\n            .antMatchers("/admin/**").hasRole("ADMIN")\n            .anyRequest().authenticated()\n            .and()\n            .formLogin();\n    }\n}',
 'Spring Security 기본 설정 예시입니다.',
 false, NOW(), NOW()),

-- 실전/운영
(2,
 (SELECT id FROM question_question WHERE map_id = 2 AND title = '테스트 코드 작성'),
 '@ExtendWith(MockitoExtension.class)\npublic class BookServiceTest {\n    @Mock\n    private BookRepository bookRepository;\n\n    @InjectMocks\n    private BookService bookService;\n\n    @Test\n    void findByIdTest() {\n        // given\n        Book book = new Book("Test Book");\n        when(bookRepository.findById(1L)).thenReturn(Optional.of(book));\n\n        // when\n        Book found = bookService.findById(1L);\n\n        // then\n        assertEquals("Test Book", found.getTitle());\n        verify(bookRepository).findById(1L);\n    }\n}',
 'JUnit5와 Mockito를 사용한 단위 테스트 예시입니다. given-when-then 패턴을 사용하여 테스트를 구조화했습니다.',
 false, NOW(), NOW()),

(2,
 (SELECT id FROM question_question WHERE map_id = 2 AND title = '성능 최적화 실습'),
 '@Repository\npublic interface BookRepository extends JpaRepository<Book, Long> {\n    @EntityGraph(attributePaths = {"authors", "category"})\n    @Query("SELECT b FROM Book b WHERE b.category.id = :categoryId")\n    List<Book> findByCategoryIdWithAuthors(@Param("categoryId") Long categoryId);\n\n    @Cacheable(value = "books", key = "#id")\n    Optional<Book> findById(Long id);\n\n    @QueryHints(value = {@QueryHint(name = "org.hibernate.readOnly", value = "true")})\n    List<Book> findAllByOrderByTitleAsc();\n}',
 'JPA 성능 최적화 예시입니다. N+1 문제 해결을 위한 EntityGraph, 캐시 적용, 읽기 전용 쿼리 힌트 등을 구현했습니다.',
 false, NOW(), NOW()),

(2,
 (SELECT id FROM question_question WHERE map_id = 2 AND title = '배포 환경 구축'),
 'pipeline {\n    agent any\n    stages {\n        stage("Build") {\n            steps {\n                sh "./gradlew clean build"\n            }\n        }\n        stage("Test") {\n            steps {\n                sh "./gradlew test"\n            }\n        }\n        stage("Docker Build") {\n            steps {\n                sh "docker build -t myapp:${BUILD_NUMBER} ."\n            }\n        }\n        stage("Deploy") {\n            steps {\n                sh "aws ecs update-service --cluster prod --service myapp --force-new-deployment"\n            }\n        }\n    }\n    post {\n        always {\n            junit "**/build/test-results/test/*.xml"\n        }\n    }\n}',
 'Jenkins 파이프라인을 사용한 CI/CD 구성 예시입니다. 빌드, 테스트, 도커 이미지 생성, AWS ECS 배포 등의 단계를 포함합니다.',
 false, NOW(), NOW()),

-- Spring Boot 진입을 위한 추가 Question들의 Answer
(2,
 (SELECT id FROM question_question WHERE map_id = 2 AND title = 'JPA 기초 실습'),
 '@Entity\npublic class Member {\n    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)\n    private Long id;\n\n    @Column(nullable = false)\n    private String name;\n\n    @ManyToOne(fetch = FetchType.LAZY)\n    @JoinColumn(name = "team_id")\n    private Team team;\n\n    // Getter, Setter\n}\n\n@Entity\npublic class Team {\n    @Id @GeneratedValue\n    private Long id;\n\n    private String name;\n\n    @OneToMany(mappedBy = "team")\n    private List<Member> members = new ArrayList<>();\n}',
 'JPA Entity 매핑의 기본 예시입니다. 일대다 관계 매핑과 지연 로딩 설정이 포함되어 있습니다.',
 false, NOW(), NOW()),

(2,
 (SELECT id FROM question_question WHERE map_id = 2 AND title = 'REST API 기초 실습'),
 '1. 회원 목록 조회\nGET /api/members\n응답: 200 OK, [{"id": 1, "name": "John"}]\n\n2. 회원 상세 조회\nGET /api/members/{id}\n응답: 200 OK, {"id": 1, "name": "John"}\n\n3. 회원 등록\nPOST /api/members\n요청: {"name": "John"}\n응답: 201 Created, {"id": 1, "name": "John"}\n\n4. 회원 정보 수정\nPUT /api/members/{id}\n요청: {"name": "John Doe"}\n응답: 200 OK, {"id": 1, "name": "John Doe"}\n\n5. 회원 삭제\nDELETE /api/members/{id}\n응답: 204 No Content',
 'RESTful API 설계 원칙을 따른 API 명세입니다. 적절한 HTTP 메서드와 응답 코드를 사용했습니다.',
 false, NOW(), NOW()),

(2,
 (SELECT id FROM question_question WHERE map_id = 2 AND title = 'Spring Data JPA 실습'),
 'public interface MemberRepository extends JpaRepository<Member, Long> {\n    // 사용자 정의 쿼리 메서드\n    List<Member> findByNameContaining(String name);\n\n    // @Query 사용\n    @Query("SELECT m FROM Member m JOIN FETCH m.team WHERE m.team.name = :teamName")\n    List<Member> findMembersWithTeam(@Param("teamName") String teamName);\n\n    // 페이징과 정렬\n    Page<Member> findByTeamName(String teamName, Pageable pageable);\n}',
 'Spring Data JPA Repository 구현 예시입니다. 메서드 이름을 통한 쿼리 생성, @Query 애노테이션, 페이징 처리가 포함되어 있습니다.',
 false, NOW(), NOW()),

(2,
 (SELECT id FROM question_question WHERE map_id = 2 AND title = 'API 문서화 실습'),
 '@Configuration\npublic class SwaggerConfig {\n    @Bean\n    public OpenAPI openAPI() {\n        return new OpenAPI()\n            .info(new Info()\n                .title("Member API")\n                .version("1.0")\n                .description("회원 관리 API 문서"));\n    }\n}\n\n@RestController\n@Tag(name = "Member API", description = "회원 관리 API")\npublic class MemberController {\n    @Operation(summary = "회원 목록 조회")\n    @ApiResponses({\n        @ApiResponse(responseCode = "200", description = "조회 성공"),\n        @ApiResponse(responseCode = "500", description = "서버 오류")\n    })\n    @GetMapping("/api/members")\n    public List<MemberResponse> getMembers() {\n        // 구현\n    }\n}',
 'Swagger/OpenAPI 설정과 애노테이션을 사용한 API 문서화 예시입니다. API 그룹화, 상세 설명, 응답 코드 설명 등이 포함되어 있습니다.',
 false, NOW(), NOW()),

-- 시작 Node들의 QuestionAnswers
(2,
 (SELECT id FROM question_question WHERE map_id = 2 AND title = 'JPA 시작하기'),
 '1. pom.xml 또는 build.gradle에 의존성 추가\n2. src/main/resources/META-INF/persistence.xml 설정\n3. EntityManagerFactory 생성 테스트',
 'JPA 학습을 위한 기본 프로젝트 구성입니다.',
 false, NOW(), NOW()),

(2,
 (SELECT id FROM question_question WHERE map_id = 2 AND title = 'REST API 시작하기'),
 '1. Postman 설치 완료\n2. Spring Boot 기반 REST API 서버 구성\n3. GET /hello 엔드포인트 테스트 성공',
 'REST API 학습을 위한 기본 환경 구성입니다.',
 false, NOW(), NOW()); 