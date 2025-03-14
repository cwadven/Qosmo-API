### 0. 00_map.sql
맵의 기본 정보를 설정합니다.

테이블 명: map_map

예제:
```sql
INSERT INTO map_map (
  name, description, icon_image, background_image,
  subscriber_count, play_count, created_by_id,
  is_private, is_deleted,
  created_at, updated_at
) VALUES (
  '연인과 여행 데이트',
  '연인과 함께 여행 데이트를 계획하는 맵입니다.',
  'https://placehold.co/600x400',
  'https://placehold.co/600x400',
  0,
  0,
  (SELECT id FROM member_member WHERE username = 'admin' LIMIT 1),
  false,
  false,
  NOW(),
  NOW()
) RETURNING id;
```

**참고:**
- icon_image와 background_image는 placeholder 이미지 사용
- created_by_id는 (SELECT id FROM member_member WHERE username = 'admin' LIMIT 1) 로 작성
- 생성된 map_id를 이후 다른 SQL 파일에서 참조

### 체크리스트
- [ ] 필수 필드가 모두 올바르게 설정됨
  - [ ] name: 맵 이름
  - [ ] description: 맵 설명
  - [ ] icon_image: 맵 아이콘 이미지 URL
  - [ ] background_image: 맵 배경 이미지 URL
  - [ ] subscriber_count: 구독자 수 (기본값 0)
  - [ ] play_count: 플레이 횟수 (기본값 0)
  - [ ] created_by_id: 생성자 ID (member_member 테이블 참조)
  - [ ] is_private: 비공개 여부
  - [ ] is_deleted: 삭제 여부
  - [ ] created_at, updated_at: 생성/수정 시간
- [ ] 생성된 map_id가 올바르게 반환됨
- [ ] 참조하는 필드가 올바르게 참조됨