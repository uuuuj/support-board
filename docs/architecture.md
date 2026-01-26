# Support Board 배포 아키텍처

## 전체 구조

```
                                    ┌─────────────────────────────────────────────────────────┐
                                    │                      Server                             │
                                    │                                                         │
    ┌──────────┐                    │  ┌─────────────────────────────────────────────────┐   │
    │          │                    │  │            Host Nginx (Reverse Proxy)           │   │
    │  Client  │ ── HTTP Request ──>│  │                   Port 80/443                   │   │
    │ (Browser)│                    │  │                                                 │   │
    │          │                    │  │   ┌─────────────────────────────────────────┐   │   │
    └──────────┘                    │  │   │            Location Routing             │   │   │
                                    │  │   │                                         │   │   │
                                    │  │   │  /embed8510/*  ──────────────────────┐  │   │   │
                                    │  │   │  /support/api/*  ─────────────────┐  │  │   │   │
                                    │  │   │  /other-app/*  ────────────────┐  │  │  │   │   │
                                    │  │   │  /another-app/*  ───────────┐  │  │  │  │   │   │
                                    │  │   └─────────────────────────────│──│──│──│──┘   │   │
                                    │  └─────────────────────────────────│──│──│──│──────┘   │
                                    │                                    │  │  │  │          │
                                    │                                    ▼  │  │  │          │
                                    │  ┌─────────────────────────────────────┐  │  │          │
                                    │  │   Other App Container               │  │  │          │
                                    │  │   127.0.0.1:8xxx                    │  │  │          │
                                    │  └─────────────────────────────────────┘  │  │          │
                                    │                                    ▼      │  │          │
                                    │  ┌─────────────────────────────────────┐  │  │          │
                                    │  │   Another App Container             │  │  │          │
                                    │  │   127.0.0.1:8xxx                    │  │  │          │
                                    │  └─────────────────────────────────────┘  │  │          │
                                    │                                           ▼  │          │
                                    │  ┌─────────────────────────────────────────────┐        │
                                    │  │        Django Backend (API Server)          │        │
                                    │  │              127.0.0.1:7000                  │        │
                                    │  │                                             │        │
                                    │  │  - /support/api/posts/                      │        │
                                    │  │  - /support/api/posts/create/               │        │
                                    │  │  - /support/api/posts/{id}/                 │        │
                                    │  └─────────────────────────────────────────────┘        │
                                    │                                              │          │
                                    │                                              ▼          │
                                    │  ┌─────────────────────────────────────────────┐        │
                                    │  │   Support Board Frontend Container          │        │
                                    │  │            127.0.0.1:8510                    │        │
                                    │  │  ┌───────────────────────────────────────┐  │        │
                                    │  │  │      Container Nginx (Static Server)  │  │        │
                                    │  │  │              Port 80                   │  │        │
                                    │  │  │                                       │  │        │
                                    │  │  │   /usr/share/nginx/html/              │  │        │
                                    │  │  │   ├── index.html                      │  │        │
                                    │  │  │   └── assets/                         │  │        │
                                    │  │  │       ├── index-xxx.js                │  │        │
                                    │  │  │       └── index-xxx.css               │  │        │
                                    │  │  └───────────────────────────────────────┘  │        │
                                    │  └─────────────────────────────────────────────┘        │
                                    │                                                         │
                                    └─────────────────────────────────────────────────────────┘
```

## 요청 흐름

### 1. 프론트엔드 페이지 요청

```
Client                    Host Nginx                 Frontend Container
  │                           │                              │
  │  GET /embed8510/          │                              │
  │ ────────────────────────> │                              │
  │                           │  proxy_pass                  │
  │                           │  127.0.0.1:8510/             │
  │                           │ ───────────────────────────> │
  │                           │                              │
  │                           │      index.html              │
  │                           │ <─────────────────────────── │
  │      index.html           │                              │
  │ <──────────────────────── │                              │
```

### 2. API 요청 (프론트엔드 → 백엔드)

```
Client                    Host Nginx                 Django Backend
  │                           │                              │
  │  GET /support/api/posts/  │                              │
  │ ────────────────────────> │                              │
  │                           │  proxy_pass                  │
  │                           │  127.0.0.1:7000              │
  │                           │ ───────────────────────────> │
  │                           │                              │
  │                           │      JSON Response           │
  │                           │ <─────────────────────────── │
  │      JSON Response        │                              │
  │ <──────────────────────── │                              │
```

## 컴포넌트 역할

| 컴포넌트 | 주소 | 역할 |
|---------|------|------|
| **Host Nginx** | 0.0.0.0:80/443 | 리버스 프록시, SSL 종료, URL 기반 라우팅 |
| **Django Backend** | 127.0.0.1:7000 | REST API 제공 |
| **Frontend Container Nginx** | 127.0.0.1:8510 | React SPA 정적 파일 서빙, SPA 라우팅 |

## 두 Nginx의 역할 차이

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              요청 흐름                                       │
│                                                                             │
│   Client ──> Host Nginx ──> Container Nginx ──> 정적 파일 (HTML/JS/CSS)    │
│              (프록시)        (웹 서버)                                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

| 구분 | Host Nginx | Container Nginx |
|------|------------|-----------------|
| **역할** | 리버스 프록시 (Reverse Proxy) | 웹 서버 (Web Server) |
| **하는 일** | 요청을 받아서 **다른 서버로 전달** | 요청을 받아서 **파일을 직접 응답** |
| **핵심 설정** | `proxy_pass http://127.0.0.1:8510/` | `root /usr/share/nginx/html` |
| **바인딩** | 0.0.0.0:80 (외부 노출) | 127.0.0.1:8510 (내부 전용) |

## 보안 구조

```
                    외부 접근 가능           │        외부 접근 불가 (127.0.0.1)
                                           │
    Internet ──────> Host Nginx ───────────┼──────> Django (127.0.0.1:7000)
                     (0.0.0.0:80)          │
                                           │──────> Frontend (127.0.0.1:8510)
                                           │
                                           │──────> Other Apps (127.0.0.1:xxxx)
```

- **127.0.0.1 바인딩**: 모든 백엔드 서비스는 localhost에만 바인딩
- **외부 직접 접근 차단**: Host Nginx를 통해서만 접근 가능
- **iframe 임베딩**: Django 페이지에서 iframe으로 프론트엔드 로드

## Nginx 설정

### Host Nginx (nginx-support-board.conf)

```nginx
# 프론트엔드 프록시
location /embed8510 {
    proxy_pass http://127.0.0.1:8510/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

# Django API 프록시
location /support/api {
    proxy_pass http://127.0.0.1:7000;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Cookie $http_cookie;
    proxy_pass_header Set-Cookie;
}
```

### Container Nginx (frontend/nginx.conf)

```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # SPA 라우팅
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 정적 자산 캐싱
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## 배포 명령어

```bash
# 이미지 로드
docker load -i support-board-frontend.tar

# 컨테이너 실행
docker run -d --name support-board-frontend \
  --restart unless-stopped \
  -p 127.0.0.1:8510:80 \
  support-board-frontend

# Nginx 설정 적용
nginx -t && systemctl reload nginx
```
