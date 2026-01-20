# Frontend Build Only (Nginx 없음)
FROM node:22-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

# 빌드 결과물만 출력 (dist 폴더)
FROM alpine:latest
COPY --from=builder /app/dist /dist
CMD ["echo", "Frontend build complete. Copy /dist to your web server."]
