# Bookmark API

A REST API for managing bookmarks, built with FastAPI and SQLAlchemy. Features JWT-based authentication so each user can only access their own bookmarks.

## Requirements

- Python 3.11+

## Setup

```bash
uv venv --python 3.11
source .venv/bin/activate
uv pip install -r requirements.txt
```

## Database

The project uses SQLite by default. Run migrations to set up the schema:

```bash
alembic upgrade head
```

### Seed data

Optionally populate the database with sample users, tags, and bookmarks:

```bash
python seed.py
```

This creates 3 users (alice, bob, charlie — all with password `password123`), 10 tags, and 12 bookmarks. The script is idempotent and will skip seeding if data already exists. To re-seed, delete `bookmarks.db` and run migrations again first.

## Running the server

```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000. Interactive docs at http://localhost:8000/docs.

## Docker deployment

Build and run with Docker Compose:

```bash
docker compose up --build
```

To set a custom secret key (recommended for production):

```bash
SECRET_KEY=my-super-secret docker compose up --build
```

Or create a `.env` file in the project root:

```
SECRET_KEY=my-super-secret
```

The database is stored in a Docker volume (`bookmark-data`) and persists across container restarts. Alembic migrations run automatically on startup.

### Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:////app/data/bookmarks.db` | SQLAlchemy database URL |
| `SECRET_KEY` | `please-change-this-secret` | Secret key for signing JWT tokens |

## Running tests

```bash
pytest
```

Tests use an in-memory SQLite database and don't require any setup.

## API overview

### Auth

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Create a new account |
| POST | `/auth/login` | Get a JWT access token (form data) |

### Users

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/users/me` | Yes | Get current user info |

### Bookmarks

All bookmark endpoints require a `Bearer` token in the `Authorization` header.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/bookmarks` | Create a bookmark |
| GET | `/bookmarks` | List your bookmarks (paginated, with filters) |
| GET | `/bookmarks/{id}` | Get a bookmark by ID |
| PATCH | `/bookmarks/{id}` | Update a bookmark |
| DELETE | `/bookmarks/{id}` | Delete a bookmark |

#### Query parameters for `GET /bookmarks`

| Parameter | Type | Description |
|-----------|------|-------------|
| `tag` | string | Filter by tag name |
| `q` | string | Search by title (case-insensitive) |
| `created_after` | datetime | Only bookmarks created after this date |
| `created_before` | datetime | Only bookmarks created before this date |
| `page` | int | Page number (default: 1) |
| `page_size` | int | Items per page, 1-100 (default: 20) |

### Tags

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/tags` | No | Create a tag |
| GET | `/tags` | No | List all tags |

## Example usage

### Register a new user

```bash
curl -s -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "email": "alice@example.com", "password": "mysecretpass"}'
```

```json
{
  "username": "alice",
  "email": "alice@example.com",
  "id": 1,
  "created_at": "2026-05-27T12:00:00"
}
```

### Log in

The login endpoint accepts **form data** (OAuth2 password flow), not JSON:

```bash
curl -s -X POST http://localhost:8000/auth/login \
  -d "username=alice&password=mysecretpass"
```

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

Export the token for subsequent requests:

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -d "username=alice&password=mysecretpass" | jq -r .access_token)
```

### Get current user

```bash
curl -s http://localhost:8000/users/me \
  -H "Authorization: Bearer $TOKEN"
```

```json
{
  "username": "alice",
  "email": "alice@example.com",
  "id": 1,
  "created_at": "2026-05-27T12:00:00"
}
```

### Create a bookmark

```bash
curl -s -X POST http://localhost:8000/bookmarks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "url": "https://fastapi.tiangolo.com",
    "title": "FastAPI Docs",
    "description": "Modern Python web framework",
    "tag_names": ["python", "web"]
  }'
```

```json
{
  "url": "https://fastapi.tiangolo.com/",
  "title": "FastAPI Docs",
  "description": "Modern Python web framework",
  "id": 1,
  "user_id": 1,
  "created_at": "2026-05-27T12:00:00",
  "updated_at": "2026-05-27T12:00:00",
  "tags": [
    {"name": "python", "id": 1},
    {"name": "web", "id": 2}
  ]
}
```

### List bookmarks (with filters and pagination)

```bash
# All bookmarks (page 1)
curl -s "http://localhost:8000/bookmarks" \
  -H "Authorization: Bearer $TOKEN"

# Filter by tag
curl -s "http://localhost:8000/bookmarks?tag=python" \
  -H "Authorization: Bearer $TOKEN"

# Search by title keyword, page 2
curl -s "http://localhost:8000/bookmarks?q=docs&page=2&page_size=5" \
  -H "Authorization: Bearer $TOKEN"
```

```json
{
  "items": [
    {
      "url": "https://fastapi.tiangolo.com/",
      "title": "FastAPI Docs",
      "description": "Modern Python web framework",
      "id": 1,
      "user_id": 1,
      "created_at": "2026-05-27T12:00:00",
      "updated_at": "2026-05-27T12:00:00",
      "tags": [
        {"name": "python", "id": 1},
        {"name": "web", "id": 2}
      ]
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20
}
```

### Update a bookmark

```bash
curl -s -X PATCH http://localhost:8000/bookmarks/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title": "FastAPI Official Docs", "tag_names": ["python", "web", "reference"]}'
```

```json
{
  "url": "https://fastapi.tiangolo.com/",
  "title": "FastAPI Official Docs",
  "description": "Modern Python web framework",
  "id": 1,
  "user_id": 1,
  "created_at": "2026-05-27T12:00:00",
  "updated_at": "2026-05-27T12:01:00",
  "tags": [
    {"name": "python", "id": 1},
    {"name": "web", "id": 2},
    {"name": "reference", "id": 3}
  ]
}
```

### Delete a bookmark

```bash
curl -s -X DELETE http://localhost:8000/bookmarks/1 \
  -H "Authorization: Bearer $TOKEN"
# Returns 204 No Content
```

### Create a tag

```bash
curl -s -X POST http://localhost:8000/tags \
  -H "Content-Type: application/json" \
  -d '{"name": "devops"}'
```

```json
{"name": "devops", "id": 1}
```

### List all tags

```bash
curl -s http://localhost:8000/tags
```

```json
[
  {"name": "devops", "id": 1},
  {"name": "python", "id": 2},
  {"name": "web", "id": 3}
]
```

## Quick demo

For a step-by-step walkthrough that exercises every endpoint, see [DEMO.md](DEMO.md).
