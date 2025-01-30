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

### 설정

1. 환경 설정

```shell
# Clone the repository

# Create a virtual environment in the root directory
python -m venv venv

# Activate the virtual environment
# Windows
source venv/Scripts/activate
# Linux
source venv/bin/activate

# Install the requirements
pip install -r requirements.txt

# Define settings file
# local, development, production
export DJANGO_SETTINGS_MODULE=XXXX.settings.xxxx
```

2. Django 환경 변수 (.django_env)

```shell
# Define .django_env file
fab2 generate-env

-- Below is the example of .django_env file creating --

-----------------0----------------------
- Input CSRF_TRUSTED_ORIGIN:
----------------------------------------
For use CSRF_TRUSTED_ORIGINS, you need to set the host ip.

"CSRF_TRUSTED_ORIGIN" Example: "http://127.0.0.1"
----------------------------------------
 
-----------------1----------------------
- Input SECRET_KEY:
----------------------------------------
This is a secret key for Django. 
You can generate it here: https://djecrety.ir/

"SECRET_KEY" Example: "django-insecure-......test..."
----------------------------------------

----------------2-----------------------
- Input KAKAO_API_KEY:
- Input KAKAO_SECRET_KEY:
- Input KAKAO_REDIRECT_URL:
----------------------------------------
You can get it here: https://developers.kakao.com/

[ More Explain ]
"KAKAO_API_KEY" Example: "4df48d962f....."
"KAKAO_SECRET_KEY" Example: "sdfaefse....."
"KAKAO_REDIRECT_URL" Example: "http://...."
----------------------------------------

----------------3-----------------------
- Input KAKAO_PAY_CID:
- Input KAKAO_PAY_SECRET_KEY:
----------------------------------------
For Kakao Pay, you need to get a separate key.
"KAKAO_PAY_CID" Example: "TC0ONETIME"
"KAKAO_PAY_SECRET_KEY" Example: "897a....."
----------------------------------------

---------------4------------------------
- Input NAVER_API_KEY:
- Input NAVER_SECRET_KEY:
- Input NAVER_REDIRECT_URL:
----------------------------------------
You can get it here: https://developers.naver.com/main/
"NAVER_API_KEY" Example: "4df48d962f....."
"NAVER_SECRET_KEY" Example: "sdfaefse....."
"NAVER_REDIRECT_URL" Example: "http://...."
----------------------------------------

----------------5-----------------------
- Input GOOGLE_CLIENT_ID:
- Input GOOGLE_SECRET_KEY:
- Input GOOGLE_REDIRECT_URL:
----------------------------------------
You can get it here: https://console.cloud.google.com/apis/credentials

"GOOGLE_CLIENT_ID" Example: "346021117315-ikur0p9aeup3i....."
"GOOGLE_SECRET_KEY" Example: "GOCSPX-i....."
"GOOGLE_REDIRECT_URL" Example: "http://127.0.0.1:8000/account/login"
----------------------------------------

----------------6-----------------------
- Input CHANNEL_HOST:
- Input CHANNEL_PORT:
----------------------------------------
Channels uses Redis as a channel layer.

"CHANNEL_HOST" Example: 127.0.0.1 (if you use docker, you need to set docker container name example 'redis')
"CHANNEL_PORT" Example: 6379
----------------------------------------

----------------7-----------------------
- Input CELERY_BROKER_URL:
- Input result_backend:
----------------------------------------
Celery uses Redis as a message broker.
Need to install Redis: https://redis.io/

"CELERY_BROKER_URL" Example: redis://localhost:6379/2  (if you use docker, you need to set docker container name example 'redis')
"result_backend" Example: redis://localhost:6379/2
----------------------------------------

----------------8-----------------------
- Input CACHEOPS_REDIS_HOST:
- Input CACHEOPS_REDIS_PORT:
- Input CACHEOPS_REDIS_DB:
----------------------------------------
Cacheops uses Redis as a cache.

"CACHEOPS_REDIS_HOST" Example: localhost  (if you use docker, you need to set docker container name example 'redis')
"CACHEOPS_REDIS_PORT" Example: 6379
"CACHEOPS_REDIS_DB" Example: 10
(redis db number)
----------------------------------------

----------------9-----------------------
- Input CACHES_LOCATION:
----------------------------------------
Cache uses location.

"CACHES_LOCATION" Example: redis://localhost:6379/1  (if you use docker, you need to set docker container name example 'redis')
----------------------------------------

-----------------10----------------------
- Input DB_ENGINE:
- Input DB_NAME:
- Input DB_USER:
- Input DB_PASSWORD:
- Input DB_HOST:
- Input DB_PORT:
- Input DB_TEST_NAME:
----------------------------------------
Database settings.

"DB_ENGINE" Example: django.db.backends.postgresql
"DB_NAME" Example: nully
"DB_USER" Example: postgres
"DB_PASSWORD" Example: postgres
"DB_HOST" Example: localhost  (if you use docker, you need to set docker container name 'postgresql14')
"DB_PORT" Example: 5432
"DB_TEST_NAME" Example: nully_test
----------------------------------------

------------------11---------------------
- Input EMAIL_HOST_USER:
- Input EMAIL_HOST_PASSWORD:
----------------------------------------
Host email settings.
Default Gmail if you want to use other email services, you need to change the settings.

"EMAIL_HOST_USER" Example: nully@gmail.com
"EMAIL_HOST_PASSWORD" Example: 1234
----------------------------------------

-----------------12---------------------
- Input AWS_IAM_ACCESS_KEY:
- Input AWS_IAM_SECRET_ACCESS_KEY:
- Input AWS_S3_BUCKET_NAME:
- Input AWS_SQS_URL:
----------------------------------------
AWS settings.

"AWS_IAM_ACCESS_KEY" Example: AKIAYXZ223G...
"AWS_IAM_SECRET_ACCESS_KEY" Example: AKIAYXZ223G...
"AWS_S3_BUCKET_NAME" Example: nully
"AWS_SQS_URL" Example: https://sqs.ap-northeast-2.amazonaws.com/1234/nully
----------------------------------------

-----------------13---------------------
- Input CRONTAB_PREFIX_COMMAND:
----------------------------------------
"CRONTAB_PREFIX_COMMAND" 
Example:
source venv/bin/activate && python manage.py
or
cd /app && newrelic-admin run-program python manage.py
----------------------------------------


-----------------14---------------------
- Input OPENAI_API_KEY:
----------------------------------------
openai api key https://platform.openai.com/settings/profile?tab=api-keys

"OPENAI_API_KEY"
----------------------------------------


-----------------15---------------------
- Input SENTRY_DSN:
----------------------------------------
sentry dns for sentry.io of your project

SENTRY_DSN
----------------------------------------


-----------------16---------------------
- Input SENTRY_ENV:
----------------------------------------
sentry environment for sentry.io of your project

SENTRY_ENV
----------------------------------------
```

3. Docker 환경 변수 (.env)

```shell
# Docker Compose를 위한 환경 변수 파일 생성
cp .env.example .env

# .env 파일에는 다음 설정들이 포함됩니다:
POSTGRES_DB=checker
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
PGADMIN_DEFAULT_EMAIL=admin@admin.com
PGADMIN_DEFAULT_PASSWORD=admin
FLOWER_USER=admin
FLOWER_PASSWORD=admin
```

4. Database 설정

```shell
# Migrate the database
python manage.py migrate
```

5. 서버 실행

```shell
# Start development server
python manage.py runserver
```

6. Celery 실행

```shell
# Run the celery worker
celery -A config worker -l INFO -P solo
````

7. Crontab 적용
```shell
# 로그 디렉토리 생성
mkdir -p /tmp/log
# Run the crontab
fab2 update-crontab
# 필요에 따라 dos2unix 설치
dos2unix command.cron
chmod 0644 command.cron
cat command.cron | crontab -
service cron restart
```

### Docker Start
```shell
# docker-compose.yml file change environment for your DJANGO_SETTINGS_MODULE

# Start the docker container
chmod +x ./deploy.sh
./deploy.sh
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
2. Create your branch from starting master (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request to the `code-review` branch
6. When Approved by the reviewer, merge the PR
7. After merging the PR, merge to `integration` branch
8. After merging to `integration` branch, and finished testing, merge to `master` branch


## Extra

### Git Hooks

- pre-commit: Run flake8
- pre-push: Push with master branch version tag

```shell
cd project_root

chmod +x ./scripts/set_git_hooks.sh
./scripts/set_git_hooks.sh
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
