# Docker & Production

## Summary
Two compose files: `docker-compose.yml` (local dev), `docker-compose-rds.yml` (AWS RDS production). Gunicorn + nginx + Celery + Redis. Certbot SSL. Memory ~822MB total.

## Compose Files

### `docker-compose.yml` — Local Dev
PostgreSQL + Redis included. Django dev server. No SSL. Volume-mounted code for live reload.

### `docker-compose-rds.yml` — Production (AWS RDS)
RDS for PostgreSQL. Gunicorn. Nginx reverse proxy. Certbot SSL auto-renewal.

## Services

### web
- **Image:** `smartenplus-app`. **Command:** `gunicorn --bind 0.0.0.0:8000 --workers 1 --threads 2 --timeout 30`
- **Memory:** 256MB. **Port:** 8000. **Restart:** always

### nginx
- **Image:** nginx:alpine. **Memory:** 64MB. **Ports:** 80, 443
- **SSL:** Certbot auto-renewal for `api.smartenplus.co.th`. **Config:** `./nginx.conf`

### celery-worker
- **Command:** `celery -A Smartenplus worker --loglevel=info --concurrency=1 --prefetch-multiplier=1 --max-tasks-per-child=50 --max-memory-per-child=150000`
- **Memory:** 256MB. **Healthcheck:** `celery inspect ping` every 30s
- **Env:** DB, Telegram (SEP_NOTIFY_bot, SEP_GROUP_ID), AWS SES

### celery-beat
- **Command:** `celery -A Smartenplus beat --loglevel=info`. **Memory:** 96MB

### redis
- **Image:** redis:7.2-alpine. **Memory:** 150MB (--maxmemory 100mb, allkeys-lru). **Persistence:** disabled

### certbot
- **Image:** certbot/certbot:latest. **Memory:** 40MB. **Auto-renewal:** every 12h

## Build & Deploy

```bash
docker-compose -f docker-compose-rds.yml build web
docker-compose -f docker-compose-rds.yml up --no-deps web -d
docker-compose -f docker-compose-rds.yml logs -f celery-worker
docker stats --no-stream
```

## Environment Variables (Production)

```bash
POSTGRES_DB_HOST=your-rds-endpoint.amazonaws.com
POSTGRES_DB_NAME=smartenplus
POSTGRES_DB_USER=postgres
POSTGRES_DB_PASSWORD=your_password
SEP_NOTIFY_bot=your_bot_token
SEP_GROUP_ID=your_group_id
AWS_SES_REGION_NAME=ap-southeast-1
AWS_SES_REGION_ENDPOINT=email.ap-southeast-1.amazonaws.com
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
DEFAULT_FROM_EMAIL=noreply@smartenplus.co.th
EMAIL_CC_RECIPIENT=support@smartenplus.co.th
ENABLE_JOURNEY_LOGGING=True
AUTO_SMARTENPLUS_API_URL=
SENTRY_DSN=
```

## Memory Budget

| Container | Memory | Notes |
|-----------|--------|-------|
| web | 256MB | Gunicorn 1 worker + 2 threads |
| celery-worker | 256MB | Concurrency 1, max 150MB per child |
| celery-beat | 96MB | Beat scheduler |
| redis | 150MB | 100MB maxmemory |
| nginx | 64MB | SSL termination |
| **Total** | **822MB** | |

## Related
- [[backend-architecture]]
- [[celery-tasks]]
