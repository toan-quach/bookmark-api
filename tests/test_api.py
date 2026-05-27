from tests.conftest import _register_and_login


# ---------------------------------------------------------------------------
# Auth – registration
# ---------------------------------------------------------------------------
def test_register(client):
    resp = client.post("/auth/register", json={
        "username": "alice", "email": "alice@example.com", "password": "password123",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == "alice"
    assert data["email"] == "alice@example.com"
    assert "id" in data and "created_at" in data
    assert "password" not in data and "password_hash" not in data


# ---------------------------------------------------------------------------
# Auth – login returns token
# ---------------------------------------------------------------------------
def test_login(client):
    client.post("/auth/register", json={
        "username": "bob", "email": "bob@example.com", "password": "password123",
    })
    resp = client.post("/auth/login", data={"username": "bob", "password": "password123"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


# ---------------------------------------------------------------------------
# Auth – wrong password returns 401
# ---------------------------------------------------------------------------
def test_login_wrong_password(client):
    client.post("/auth/register", json={
        "username": "carol", "email": "carol@example.com", "password": "password123",
    })
    resp = client.post("/auth/login", data={"username": "carol", "password": "wrong"})
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Auth – duplicate username returns 409
# ---------------------------------------------------------------------------
def test_duplicate_username(client):
    client.post("/auth/register", json={
        "username": "dave", "email": "dave@example.com", "password": "password123",
    })
    resp = client.post("/auth/register", json={
        "username": "dave", "email": "other@example.com", "password": "password123",
    })
    assert resp.status_code == 409
    assert resp.json()["error"] == "Username already taken"


# ---------------------------------------------------------------------------
# Auth – short password rejected
# ---------------------------------------------------------------------------
def test_short_password(client):
    resp = client.post("/auth/register", json={
        "username": "eve", "email": "eve@example.com", "password": "short",
    })
    assert resp.status_code == 422
    assert any("8 characters" in d["message"] for d in resp.json()["details"])


# ---------------------------------------------------------------------------
# Auth – unauthenticated request returns 403
# ---------------------------------------------------------------------------
def test_unauthenticated_access(client):
    resp = client.get("/bookmarks")
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Users – get current user
# ---------------------------------------------------------------------------
def test_get_me(client, auth_headers):
    resp = client.get("/users/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["username"] == "testuser"


# ---------------------------------------------------------------------------
# Bookmarks – full CRUD cycle
# ---------------------------------------------------------------------------
def test_bookmark_crud(client, auth_headers):
    resp = client.post(
        "/bookmarks",
        json={"url": "https://example.com", "title": "Ex", "description": "desc", "tag_names": ["web"]},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    bm = resp.json()
    bid = bm["id"]
    assert bm["title"] == "Ex"
    assert len(bm["tags"]) == 1

    resp = client.get(f"/bookmarks/{bid}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["title"] == "Ex"

    resp = client.patch(f"/bookmarks/{bid}", json={"title": "Updated"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated"

    resp = client.delete(f"/bookmarks/{bid}", headers=auth_headers)
    assert resp.status_code == 204

    resp = client.get(f"/bookmarks/{bid}", headers=auth_headers)
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Bookmarks – filter by tag
# ---------------------------------------------------------------------------
def test_filter_by_tag(client, auth_headers):
    client.post("/bookmarks", json={"url": "https://a.com", "title": "A", "tag_names": ["alpha"]}, headers=auth_headers)
    client.post("/bookmarks", json={"url": "https://b.com", "title": "B", "tag_names": ["beta"]}, headers=auth_headers)

    resp = client.get("/bookmarks", params={"tag": "alpha"}, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "A"


# ---------------------------------------------------------------------------
# Bookmarks – search by keyword
# ---------------------------------------------------------------------------
def test_search_by_keyword(client, auth_headers):
    client.post("/bookmarks", json={"url": "https://a.com", "title": "FastAPI Guide"}, headers=auth_headers)
    client.post("/bookmarks", json={"url": "https://b.com", "title": "Django Tutorial"}, headers=auth_headers)

    resp = client.get("/bookmarks", params={"q": "fast"}, headers=auth_headers)
    data = resp.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert "FastAPI" in data["items"][0]["title"]


# ---------------------------------------------------------------------------
# Bookmarks – user isolation (can't see other user's bookmarks)
# ---------------------------------------------------------------------------
def test_user_isolation(client):
    h1 = _register_and_login(client, "user1", "u1@example.com", "password123")
    h2 = _register_and_login(client, "user2", "u2@example.com", "password123")

    resp = client.post("/bookmarks", json={"url": "https://secret.com", "title": "Secret"}, headers=h1)
    bid = resp.json()["id"]

    resp = client.get(f"/bookmarks/{bid}", headers=h2)
    assert resp.status_code == 404

    resp = client.get("/bookmarks", headers=h2)
    assert resp.json()["items"] == []
    assert resp.json()["total"] == 0


# ---------------------------------------------------------------------------
# Bookmarks – update replaces tags
# ---------------------------------------------------------------------------
def test_update_replaces_tags(client, auth_headers, bookmark):
    bid = bookmark["id"]
    assert {t["name"] for t in bookmark["tags"]} == {"dev", "python"}

    resp = client.patch(f"/bookmarks/{bid}", json={"tag_names": ["rust"]}, headers=auth_headers)
    assert resp.status_code == 200
    assert [t["name"] for t in resp.json()["tags"]] == ["rust"]


# ---------------------------------------------------------------------------
# Validation – invalid tag name rejected
# ---------------------------------------------------------------------------
def test_invalid_tag_name(client, auth_headers):
    resp = client.post(
        "/bookmarks",
        json={"url": "https://example.com", "title": "OK", "tag_names": ["good", "BAD TAG!"]},
        headers=auth_headers,
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Validation – empty bookmark title rejected
# ---------------------------------------------------------------------------
def test_empty_bookmark_title(client, auth_headers):
    resp = client.post(
        "/bookmarks",
        json={"url": "https://example.com", "title": "   "},
        headers=auth_headers,
    )
    assert resp.status_code == 422
    assert any("empty" in d["message"].lower() for d in resp.json()["details"])


# ---------------------------------------------------------------------------
# Validation – short username rejected
# ---------------------------------------------------------------------------
def test_username_too_short(client):
    resp = client.post("/auth/register", json={
        "username": "ab", "email": "x@y.com", "password": "password123",
    })
    assert resp.status_code == 422
    assert any("at least 3" in d["message"] for d in resp.json()["details"])


# ---------------------------------------------------------------------------
# Validation – invalid email rejected
# ---------------------------------------------------------------------------
def test_invalid_email(client):
    resp = client.post("/auth/register", json={
        "username": "validname", "email": "not-an-email", "password": "password123",
    })
    assert resp.status_code == 422
    assert any(d["field"] == "email" for d in resp.json()["details"])
