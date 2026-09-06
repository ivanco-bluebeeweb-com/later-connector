# Later Connector — Discovery & API Specification

**Vendor:** Later  
**Catalog URL:** https://later.com  
**API Base URL:** `https://api.later.com/v1`  
**Authentication:** OAuth 2.0 Bearer Token

## Core Entities & Endpoints
профили социальных сетей, медиа-библиотека (/media), запланированные посты (/posts), аналитика

## Verified Read Operation
- **Эндпоинт проверки:** `GET /v1/users/me/social_profiles`
- **Метод:** GET
- **Ожидаемый ответ:** HTTP 200 OK со структурой метаданных сущности.

## Rate Limits & Pagination
- Стандартная курсорная или offset/limit пагинация вендора.
- Обработка HTTP 429 Too Many Requests с экспоненциальным backoff.
- Защита от тайм-аутов: ограничение на сетевые запросы 15-30 секунд.
