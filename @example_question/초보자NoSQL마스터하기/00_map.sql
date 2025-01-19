-- NoSQL 학습 맵 생성
INSERT INTO map_map (
  name, description, icon_image, background_image,
  subscriber_count, view_count, created_by_id,
  is_private, is_deleted,
  created_at, updated_at
) VALUES (
  '초보자도 따라해서 마스터 할 수 있는 NoSQL',
  'NoSQL 데이터베이스의 기초부터 실전까지 마스터하는 학습 로드맵입니다. MongoDB, Redis, Cassandra 등 주요 NoSQL 데이터베이스를 다룹니다.',
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