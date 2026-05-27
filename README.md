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

## Running the server

```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000. Interactive docs at http://localhost:8000/docs.

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
| POST | `/auth/login` | Get a JWT access token |

### Users

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/users/me` | Yes | Get current user info |

### Bookmarks

All bookmark endpoints require a `Bearer` token in the `Authorization` header.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/bookmarks` | Create a bookmark |
| GET | `/bookmarks` | List your bookmarks (supports `?tag=`, `?q=`, `?created_after=`, `?created_before=`) |
| GET | `/bookmarks/{id}` | Get a bookmark |
| PATCH | `/bookmarks/{id}` | Update a bookmark |
| DELETE | `/bookmarks/{id}` | Delete a bookmark |

### Tags

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/tags` | Create a tag |
| GET | `/tags` | List all tags |

## Example usage

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "email": "alice@example.com", "password": "mysecretpass"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "mysecretpass"}'
# Returns: {"access_token": "eyJ...", "token_type": "bearer"}

# Create a bookmark (use the token from login)
curl -X POST http://localhost:8000/bookmarks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJ..." \
  -d '{"url": "https://fastapi.tiangolo.com", "title": "FastAPI Docs", "tag_names": ["python", "web"]}'

# List your bookmarks
curl http://localhost:8000/bookmarks \
  -H "Authorization: Bearer eyJ..."
```
