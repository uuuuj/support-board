# Support Board

Django + React(Vite) 기반의 지원 게시판 애플리케이션입니다.

기존 Django 프로젝트에 앱으로 통합할 수 있도록 설계되었습니다.

## 기술 스택

| 구분 | 기술 |
|------|------|
| Backend | Python 3.12, Django 5.x, Django REST Framework |
| Frontend | React 19, Vite 7, Tailwind CSS 4 |
| Database | Microsoft SQL Server (MSSQL) |
| 아이콘 | Lucide React |
| 문서화 | drf-spectacular (Swagger) |

## 주요 기능

- **게시글 CRUD**: 게시글 작성, 조회, 수정, 삭제
- **댓글**: 게시글에 댓글 작성
- **비밀글**: 작성자와 관리자만 조회 가능한 비밀글 기능
- **태그 검색**: 태그 기반 게시글 필터링
- **WebSocket 유저 동기화**: 클라이언트 WebSocket 서버에서 유저 정보를 가져와 세션에 저장

## 프로젝트 구조

```
support-board/
├── config/                     # Django 프로젝트 설정
│   ├── settings.py             # Django 설정
│   ├── urls.py                 # 루트 URL 설정
│   └── wsgi.py                 # WSGI 설정
│
├── support_board/              # Django 앱
│   ├── migrations/             # DB 마이그레이션 파일
│   ├── static/support_board/   # React 빌드 결과물
│   ├── templates/support_board/
│   │   └── index.html          # React 앱을 로드하는 Django 템플릿
│   ├── models.py               # 데이터 모델 (User, Post, Comment, Tag)
│   ├── views.py                # API 뷰 (요청/응답 처리)
│   ├── services.py             # 서비스 레이어 (비즈니스 로직)
│   ├── validators.py           # 입력 검증 로직
│   ├── serializers.py          # DRF 시리얼라이저
│   ├── urls.py                 # 앱 URL 설정
│   └── tests.py                # Django API 테스트
│
├── src/                        # React 소스 코드
│   ├── main.jsx                # React 엔트리 포인트
│   ├── userSync.js             # WebSocket 유저 동기화 클라이언트
│   ├── index.css               # 전역 스타일 (Tailwind)
│   └── test/                   # 프론트엔드 테스트
│
├── tests/                      # 통합 테스트
│   └── test_integration.py     # WebSocket → API → DB 통합 테스트
│
├── mock_ws_server.py           # 테스트용 Mock WebSocket 서버
├── Dockerfile                  # Docker 이미지 설정
├── docker-compose.yml          # Docker Compose 설정
├── package.json                # npm 의존성
├── requirements.txt            # Python 의존성
└── vite.config.js              # Vite 빌드 설정
```

## 환경 변수 설정

프로젝트 루트에 `.env` 파일을 생성하고 필요한 환경 변수를 설정합니다.

`.env.example` 파일을 참고하세요.

## Docker로 실행

### 실행

```bash
# 빌드 및 실행
docker-compose up -d --build

# 로그 확인
docker-compose logs -f

# 중지
docker-compose down
```

### 마이그레이션

```bash
docker-compose exec web python manage.py migrate
```

### 접속

- 애플리케이션: http://localhost:8000/support/
- Swagger API 문서: http://localhost:8000/support/api/swagger/

## 로컬 개발

### 사전 요구사항

- Python 3.12+
- Node.js 20+
- MSSQL 서버 접근 가능

### 설치 및 실행

```bash
# 1. Python 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Python 의존성 설치
pip install -r requirements.txt

# 3. npm 의존성 설치
npm install

# 4. 환경 변수 설정
cp .env.example .env  # .env 파일 편집

# 5. Django 마이그레이션
python manage.py migrate

# 6. React 빌드
npm run build

# 7. Django 서버 실행
python manage.py runserver
```

### 개발 모드 (React HMR)

```bash
# 터미널 1: Vite 개발 서버
npm run dev

# 터미널 2: Django 서버
python manage.py runserver
```

## API 엔드포인트

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/support/api/posts/` | 게시글 목록 조회 |
| POST | `/support/api/posts/create/` | 게시글 생성 |
| GET | `/support/api/posts/{id}/` | 게시글 상세 조회 |
| PUT | `/support/api/posts/{id}/` | 게시글 수정 |
| DELETE | `/support/api/posts/{id}/` | 게시글 삭제 |
| GET | `/support/api/posts/{id}/comments/` | 댓글 목록 조회 |
| POST | `/support/api/posts/{id}/comments/` | 댓글 작성 |
| POST | `/support/api/users/sync/` | WebSocket 유저 정보 동기화 |
| GET | `/support/api/users/me/` | 현재 세션 유저 정보 |
| GET | `/support/api/tags/` | 태그 목록 조회 |

## 테스트

### Django API 테스트

```bash
# 로컬
python manage.py test support_board --keepdb

# Docker
docker-compose exec web python manage.py test support_board --keepdb
```

> **주의**: `--keepdb` 플래그를 사용해야 합니다. DB 유저에게 CREATE DATABASE 권한이 없으면 테스트 DB를 자동 생성할 수 없습니다. MSSQL에서 테스트용 DB를 미리 수동으로 생성해주세요.

### 프론트엔드 테스트

```bash
npm test
```

### 보안 테스트

보안 도구 설치:
```bash
pip install -r requirements-dev.txt
```

개별 도구 실행:
```bash
# Bandit - 보안 취약점 스캔
bandit -r support_board config

# pip-audit - 의존성 취약점 검사
pip-audit

# Safety - 의존성 취약점 검사
safety check

# Flake8 - 코드 품질
flake8 support_board config

# detect-secrets - 민감정보 탐지
detect-secrets scan --all-files
```

전체 보안 검사 스크립트:
```bash
python scripts/security_check.py
```

HTML 보안 리포트 생성:
```bash
python scripts/security_report.py
# security_reports/index.html 에서 결과 확인
```

## WebSocket 유저 동기화

이 애플리케이션은 클라이언트 PC에서 실행되는 WebSocket 서버에서 유저 정보를 가져오는 방식으로 인증합니다.

### 동작 방식

1. 프론트엔드가 로컬 WebSocket 서버에 연결
2. 유저 정보 요청
3. 받은 유저 정보를 Django API로 전송
4. Django가 세션에 유저 정보 저장
5. 주기적으로 폴링하여 유저 정보 갱신

### 테스트용 Mock WebSocket 서버

```bash
python mock_ws_server.py
```

## 비밀글 기능

- 게시글 작성 시 `is_private: true`로 비밀글 설정 가능
- 비밀글은 **작성자**와 **관리자**만 조회 가능
- 다른 유저가 비밀글 조회 시 403 Forbidden 반환

## 기존 Django 프로젝트에 통합

### 1. 앱 복사

`support_board/` 폴더를 기존 프로젝트에 복사합니다.

### 2. settings.py 수정

```python
INSTALLED_APPS = [
    # ... 기존 앱들
    'rest_framework',
    'drf_spectacular',
    'support_board',
]
```

### 3. urls.py 수정

```python
from django.urls import path, include

urlpatterns = [
    # ... 기존 URL들
    path('support/', include('support_board.urls')),
]
```

### 4. Static 파일 수집 (프로덕션)

```bash
python manage.py collectstatic
```

## npm 스크립트

| 명령어 | 설명 |
|--------|------|
| `npm run dev` | Vite 개발 서버 실행 (HMR) |
| `npm run build` | 프로덕션 빌드 |
| `npm run lint` | ESLint 실행 |
| `npm test` | 프론트엔드 테스트 실행 |

## Docker 빌드가 필요한 경우

**빌드 필요:**
- `Dockerfile`, `docker-compose.yml` 변경
- `package.json`, `package-lock.json` 변경
- `requirements.txt` 변경

**재시작만 필요:**
- Python 코드 (`.py`) 변경
- JavaScript 코드 (`.js`, `.jsx`) 변경
- 설정 파일 변경

```bash
# 코드만 변경한 경우
docker-compose restart

# 패키지나 Dockerfile 변경한 경우
docker-compose up -d --build
```
