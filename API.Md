## 📡 API Documentation

### `POST /webhook`

Receives GitHub webhook events

**Request:**

```json
{
  "ref": "refs/heads/main",
  "repository": { "name": "repo", "full_name": "user/repo" },
  "pusher": { "name": "username" },
  "commits": [
    {
      "id": "abc123",
      "message": "commit message",
      "author": { "name": "Author" },
      "timestamp": "2026-01-30T10:00:00Z"
    }
  ]
}
```

**Response:**

```json
{
  "status": "success",
  "action": "PUSH",
  "id": "677b5d605d2a2c328ce4e5e0"
}
```

---

### `GET /events`

Returns recent events (50 limit, newest first)

**Response:**

```json
{
  "events": [
    {
      "_id": "677b5d605d2a2c328ce4e5e0",
      "action": "PUSH",
      "author": "Vamsi_0",
      "to_branch": "main",
      "timestamp": "2026-01-29T20:59:00.000Z"
    }
  ]
}
```

---

### `GET /health`

Health check endpoint

**Response:**

```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2026-01-30T10:00:00.000Z"
}
```
