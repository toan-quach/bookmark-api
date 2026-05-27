"""Populate the database with mock data."""

from app.auth import hash_password
from app.db.session import engine, SessionLocal
from app.models.models import Base, Bookmark, Tag, User

USERS = [
    {"username": "alice", "email": "alice@example.com", "password": "password123"},
    {"username": "bob", "email": "bob@example.com", "password": "password123"},
    {"username": "charlie", "email": "charlie@example.com", "password": "password123"},
]

TAGS = [
    "python",
    "javascript",
    "devops",
    "tutorial",
    "reference",
    "blog",
    "video",
    "tool",
    "news",
    "ai",
]

BOOKMARKS = [
    {
        "user": "alice",
        "url": "https://docs.python.org/3/",
        "title": "Python 3 Documentation",
        "description": "Official Python documentation",
        "tags": ["python", "reference"],
    },
    {
        "user": "alice",
        "url": "https://fastapi.tiangolo.com/",
        "title": "FastAPI Docs",
        "description": "Modern Python web framework",
        "tags": ["python", "reference", "tool"],
    },
    {
        "user": "alice",
        "url": "https://realpython.com/",
        "title": "Real Python",
        "description": "Python tutorials and articles",
        "tags": ["python", "tutorial", "blog"],
    },
    {
        "user": "alice",
        "url": "https://news.ycombinator.com/",
        "title": "Hacker News",
        "description": "Tech news aggregator",
        "tags": ["news"],
    },
    {
        "user": "bob",
        "url": "https://developer.mozilla.org/",
        "title": "MDN Web Docs",
        "description": "Web development references",
        "tags": ["javascript", "reference"],
    },
    {
        "user": "bob",
        "url": "https://react.dev/",
        "title": "React Documentation",
        "description": "Official React docs",
        "tags": ["javascript", "reference"],
    },
    {
        "user": "bob",
        "url": "https://www.youtube.com/c/Fireship",
        "title": "Fireship YouTube",
        "description": "Short dev tutorials",
        "tags": ["javascript", "video", "tutorial"],
    },
    {
        "user": "bob",
        "url": "https://github.com/",
        "title": "GitHub",
        "description": "Code hosting platform",
        "tags": ["tool", "devops"],
    },
    {
        "user": "charlie",
        "url": "https://kubernetes.io/docs/",
        "title": "Kubernetes Docs",
        "description": "Container orchestration docs",
        "tags": ["devops", "reference"],
    },
    {
        "user": "charlie",
        "url": "https://www.terraform.io/",
        "title": "Terraform",
        "description": "Infrastructure as code tool",
        "tags": ["devops", "tool"],
    },
    {
        "user": "charlie",
        "url": "https://huggingface.co/",
        "title": "Hugging Face",
        "description": "ML models and datasets",
        "tags": ["ai", "tool"],
    },
    {
        "user": "charlie",
        "url": "https://arxiv.org/",
        "title": "arXiv",
        "description": "Research paper preprints",
        "tags": ["ai", "reference"],
    },
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if db.query(User).first():
        print("Database already has data — skipping seed.")
        db.close()
        return

    tag_map = {}
    for name in TAGS:
        tag = Tag(name=name)
        db.add(tag)
        tag_map[name] = tag

    user_map = {}
    for u in USERS:
        user = User(
            username=u["username"],
            email=u["email"],
            password_hash=hash_password(u["password"]),
        )
        db.add(user)
        user_map[u["username"]] = user

    db.flush()

    for b in BOOKMARKS:
        bookmark = Bookmark(
            url=b["url"],
            title=b["title"],
            description=b["description"],
            user_id=user_map[b["user"]].id,
            tags=[tag_map[t] for t in b["tags"]],
        )
        db.add(bookmark)

    db.commit()
    db.close()

    print(f"Seeded {len(USERS)} users, {len(TAGS)} tags, {len(BOOKMARKS)} bookmarks.")
    print("All users have password: password123")


if __name__ == "__main__":
    seed()
