# Checker Backend

체계적인 로드맵 기반의 진도 관리 플랫폼 Checker의 백엔드 서버입니다.

## Features

### 로드맵 (Map)

- 노드 기반의 진행 경로 제공
- 진행 상태 추적
- 로드맵 구독 및 공유 기능
- 인기 로드맵 추천

### 진행 노드 (Node)

- 단계별 컨텐츠 제공
- 노드 상태 관리 (완료, 진행 중, 잠김)
- 선행 조건 설정
- 진도율 추적

### 문제 및 평가 (Question)

- 다양한 유형의 문제 지원
  - 텍스트 기반 답변
  - 파일 제출
  - 자동/수동 채점
- 상세한 피드백 제공
- 진행 이력 관리

### 소셜 기능

![KakaoTalk](https://img.shields.io/badge/kakaotalk-ffcd00.svg?style=for-the-badge&logo=kakaotalk&logoColor=000000)
![Google](https://img.shields.io/badge/google-4285F4?style=for-the-badge&logo=google&logoColor=white)
![Naver](https://img.shields.io/badge/Naver-03C75A?style=for-the-badge&logo=naver&logoColor=white)

- 소셜 로그인 지원
- 프로필 관리
- 진행 현황 공유

## Tech Stack

### Backend

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) Version 3.12
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)

### Database

![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white) Version 14
![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)

### Infrastructure

![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)

- S3: 파일 저장소
- SQS: 메시지 큐

### CI/CD

![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)

## Getting Started

```shell
# Clone the repository
git clone https://github.com/your-username/checker-be.git

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux
source venv/Scripts/activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env file with your configuration

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver
```

## Project Structure

```
checker-be/
├── map/                    # 맵 관련 기능
│   ├── models/            # 맵, 노드, 화살표 등 모델
│   ├── views/             # API 뷰
│   └── services/          # 비즈니스 로직
├── question/              # 문제 관련 기능
│   ├── models.py          # 문제, 답변 모델
│   └── validators/        # 답변 검증 로직
├── member/                # 회원 관리
│   ├── models.py          # 회원 모델
│   └── auth/              # 인증 관련 로직
└── docs/                  # API 문서
    └── swagger/           # Swagger 명세
```

## API Documentation

API 문서는 Swagger UI를 통해 제공됩니다.

### Swagger UI 접근

- 개발 서버: `http://localhost:8000/swagger/`
- API 스키마: `http://localhost:8000/swagger.yaml`

### API 문서 업데이트

API 문서는 `docs/Swagger/swagger.yaml` 파일을 통해 관리됩니다.

## Testing

```shell
# Run tests
python manage.py test

# Run with coverage
coverage run manage.py test
coverage report
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
