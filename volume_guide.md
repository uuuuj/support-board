# Docker 볼륨 마운트 구조

## 기본 개념

```
호스트(내 PC)              컨테이너 내부
    │                          │
    │    볼륨 마운트            │
    │  ─────────────────▶      │
    │                          │
./support_board/    ═══▶  /app/support_board/
./config/           ═══▶  /app/config/
./manage.py         ═══▶  /app/manage.py
./.env              ═══▶  /app/.env
```

## 볼륨 마운트 문법

```yaml
volumes:
  - 호스트경로:컨테이너경로
  - ./support_board:/app/support_board
       │                 │
       │                 └── 컨테이너 안 경로 (Dockerfile WORKDIR 기준)
       └── 내 PC 경로 (docker-compose.yml 기준 상대경로)
```

## 프로젝트 구조

### 호스트 (내 PC)

```
project/
├── docker-compose.yml
├── Dockerfile
├── manage.py
├── requirements.txt
├── .env
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── support_board/
│   ├── models.py
│   ├── views.py
│   └── static/
├── src/                 # React 소스
└── package.json
```

### 컨테이너 내부

```
/app/                    # WORKDIR
├── manage.py
├── .env
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── support_board/
    ├── models.py
    ├── views.py
    └── static/
```

## docker-compose.yml 설정

```yaml
services:
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./.env:/app/.env:ro              # 환경변수 (읽기전용)
      - ./config:/app/config             # Django 설정
      - ./support_board:/app/support_board  # Django 앱
      - ./manage.py:/app/manage.py       # manage.py
    restart: unless-stopped
```

## /app 경로의 출처

Dockerfile에서 지정:

```dockerfile
WORKDIR /app   # 이 줄이 /app을 작업 디렉토리로 설정

COPY config/ ./config/           # → /app/config/
COPY support_board/ ./support_board/  # → /app/support_board/
COPY manage.py ./                # → /app/manage.py
```

## 수정 시 반영 방식

| 수정 대상 | 볼륨 마운트 | 반영 방식 |
|-----------|-------------|----------|
| Django 코드 | O | 자동 반영 |
| .env 파일 | O | 컨테이너 재시작 |
| React 코드 (src/) | X | 이미지 재빌드 필요 |
| requirements.txt | X | 이미지 재빌드 필요 |
| Dockerfile | - | 이미지 재빌드 필요 |

## 자주 쓰는 명령어

```bash
# 코드 수정 후 (Django) - 볼륨 마운트 되어있으면 자동 반영
# 아무것도 안 해도 됨

# .env 수정 후
docker-compose restart

# React 코드 또는 requirements.txt 수정 후
docker-compose up -d --build

# 컨테이너 내부 확인
docker exec -it 컨테이너명 bash
pwd        # /app 출력
ls         # config/ support_board/ manage.py 등
```