# Quick demo flow

A single copy-paste sequence that exercises every endpoint. Start the server first (`uvicorn app.main:app --reload`), then run each step in order.

**Step 1 — Register a user** (`POST /auth/register`)

```bash
curl -s -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "demo", "email": "demo@example.com", "password": "demo1234"}'
```

**Step 2 — Log in and capture the token** (`POST /auth/login`)

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -d "username=demo&password=demo1234" | jq -r .access_token)
echo $TOKEN
```

**Step 3 — Verify your identity** (`GET /users/me`)

```bash
curl -s http://localhost:8000/users/me \
  -H "Authorization: Bearer $TOKEN" | jq
```

**Step 4 — Create a couple of tags** (`POST /tags`)

```bash
curl -s -X POST http://localhost:8000/tags \
  -H "Content-Type: application/json" \
  -d '{"name": "python"}' | jq

curl -s -X POST http://localhost:8000/tags \
  -H "Content-Type: application/json" \
  -d '{"name": "tutorial"}' | jq
```

**Step 5 — List all tags** (`GET /tags`)

```bash
curl -s http://localhost:8000/tags | jq
```

**Step 6 — Create two bookmarks** (`POST /bookmarks`)

```bash
curl -s -X POST http://localhost:8000/bookmarks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "url": "https://docs.python.org/3/tutorial/",
    "title": "Python Tutorial",
    "description": "Official Python 3 tutorial",
    "tag_names": ["python", "tutorial"]
  }' | jq

curl -s -X POST http://localhost:8000/bookmarks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "url": "https://fastapi.tiangolo.com",
    "title": "FastAPI Docs",
    "description": "Modern async web framework",
    "tag_names": ["python"]
  }' | jq
```

**Step 7 — List all bookmarks** (`GET /bookmarks`)

```bash
curl -s "http://localhost:8000/bookmarks" \
  -H "Authorization: Bearer $TOKEN" | jq
```

**Step 8 — Filter by tag and search by title** (`GET /bookmarks?tag=...&q=...`)

```bash
# Only bookmarks tagged "tutorial"
curl -s "http://localhost:8000/bookmarks?tag=tutorial" \
  -H "Authorization: Bearer $TOKEN" | jq

# Search titles containing "fast"
curl -s "http://localhost:8000/bookmarks?q=fast" \
  -H "Authorization: Bearer $TOKEN" | jq
```

**Step 9 — Get a single bookmark** (`GET /bookmarks/{id}`)

```bash
curl -s http://localhost:8000/bookmarks/1 \
  -H "Authorization: Bearer $TOKEN" | jq
```

**Step 10 — Update a bookmark** (`PATCH /bookmarks/{id}`)

```bash
curl -s -X PATCH http://localhost:8000/bookmarks/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title": "Python 3 Official Tutorial", "tag_names": ["python", "tutorial", "reference"]}' | jq
```

**Step 11 — Delete a bookmark** (`DELETE /bookmarks/{id}`)

```bash
curl -s -o /dev/null -w "%{http_code}" -X DELETE http://localhost:8000/bookmarks/2 \
  -H "Authorization: Bearer $TOKEN"
# Expected: 204
```

**Step 12 — Confirm deletion** (`GET /bookmarks`)

```bash
curl -s "http://localhost:8000/bookmarks" \
  -H "Authorization: Bearer $TOKEN" | jq
# Only bookmark 1 remains
```
