# Support Board

Django + React(Vite) 기반의 지원 게시판 애플리케이션입니다.

기존 Django 프로젝트에 앱으로 통합할 수 있도록 설계되었습니다.

## 기술 스택

| 구분 | 기술 |
|------|------|
| Backend | Python 3.12, Django 6.0 |
| Frontend | React 19, Vite 7, Tailwind CSS 4 |
| 아이콘 | Lucide React |

## 프로젝트 구조

```
support-board/
├── config/                     # Django 프로젝트 설정 (임시, 통합 시 불필요)
│   ├── settings.py             # Django 설정
│   ├── urls.py                 # 루트 URL 설정
│   ├── wsgi.py                 # WSGI 설정
│   └── asgi.py                 # ASGI 설정
│
├── support_board/              # Django 앱 (기존 프로젝트에 복사할 부분)
│   ├── migrations/             # DB 마이그레이션 파일
│   ├── static/support_board/   # React 빌드 결과물
│   │   ├── assets/             # 빌드된 JS/CSS 파일
│   │   └── .vite/manifest.json # Vite 빌드 매니페스트
│   ├── templates/support_board/
│   │   └── index.html          # React 앱을 로드하는 Django 템플릿
│   ├── models.py               # 데이터 모델
│   ├── views.py                # 뷰 (요청/응답 처리)
│   ├── services.py             # 서비스 레이어 (비즈니스 로직)
│   ├── urls.py                 # 앱 URL 설정
│   └── admin.py                # 관리자 페이지 설정
│
├── src/                        # React 소스 코드
│   ├── main.jsx                # React 엔트리 포인트
│   └── index.css               # 전역 스타일 (Tailwind)
│
├── public/                     # 정적 파일
├── manage.py                   # Django 관리 명령어
├── package.json                # npm 의존성
├── vite.config.js              # Vite 빌드 설정
├── tailwind.config.js          # Tailwind CSS 설정
└── .claude/CLADUE.md           # 코드 작성 컨벤션
```

## 로컬 개발

### 사전 요구사항

- Python 3.12+
- Node.js 18+
- Django가 설치된 Python 가상환경

### 설치 및 실행

```bash
# 1. 의존성 설치
npm install

# 2. 가상환경 활성화
source ~/Developer/python312_venv/bin/activate

# 3. Django 마이그레이션
python manage.py migrate

# 4. React 빌드
npm run build

# 5. Django 서버 실행
python manage.py runserver

# 6. 브라우저에서 접속
# http://localhost:8000/support/
```

### 개발 모드 (React HMR)

React 개발 시 HMR(Hot Module Replacement)을 사용하려면:

```bash
# 터미널 1: Vite 개발 서버
npm run dev

# 터미널 2: Django 서버
python manage.py runserver
```

manifest.json이 없으면 템플릿이 자동으로 `localhost:5173`의 Vite 개발 서버를 참조합니다.

## 기존 Django 프로젝트에 통합

### 1. 앱 복사

`support_board/` 폴더를 기존 프로젝트에 복사합니다.

### 2. settings.py 수정

```python
INSTALLED_APPS = [
    # ... 기존 앱들
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

## 주요 파일 설명

### Django 측

| 파일 | 설명 |
|------|------|
| `views.py` | React SPA를 서빙하는 뷰. Vite manifest를 파싱하여 빌드 파일 경로를 템플릿에 전달 |
| `services.py` | `ViteManifestService` - manifest.json 파싱 로직을 담당하는 서비스 클래스 |
| `urls.py` | `/support/` 경로로 index 뷰 라우팅 |
| `templates/.../index.html` | React 앱을 마운트하는 HTML 템플릿 |

### React/Vite 측

| 파일 | 설명 |
|------|------|
| `vite.config.js` | 빌드 출력 경로를 `support_board/static/support_board/`로 설정 |
| `src/main.jsx` | React 앱 엔트리 포인트 |
| `src/index.css` | Tailwind CSS를 포함한 전역 스타일 |

## npm 스크립트

| 명령어 | 설명 |
|--------|------|
| `npm run dev` | Vite 개발 서버 실행 (HMR) |
| `npm run build` | 프로덕션 빌드 → `support_board/static/support_board/` |
| `npm run lint` | ESLint 실행 |
| `npm run preview` | 빌드 결과물 미리보기 |

## 코드 컨벤션

`.claude/CLADUE.md` 파일에 정의된 규칙을 따릅니다:

- **Django**: Service 레이어 분리, Google Style Docstring, Type Hints
- **React**: 단일 책임 원칙, JSDoc 주석, 정해진 코드 구성 순서
