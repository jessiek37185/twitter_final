# Twitter Final Project
[![](https://github.com/Jessiek37185/twitter_final/actions/workflows/test.yml/badge.svg)](https://github.com/Jessiek37185/twitter_final/actions?query=workflow%3Atest)


A Dockerized Twitter-style Flask web application using PostgreSQL full-text search and RUM indexes.

## Features

- Flask web application
- PostgreSQL database
- User authentication
- Create accounts
- Create messages
- Chronological message feed
- Full-text search
- Search ranking with `ts_rank`
- Highlighted search results with `ts_headline`
- Dockerized development environment
- Production nginx setup
- SQL injection prevention using parameterized queries

---

# Development Setup

## Start containers

```bash
docker compose up --build
```

---

# Open the app

Visit:

```text
http://localhost:9898
```

Or on lambda:

```text
http://lambda.compute.cmc.edu:9898
```

---

# Database Schema

The database schema is automatically loaded from:

```text
services/postgres/schema.sql
```

---

# Project Structure

```text
.
├── docker-compose.yml
├── docker-compose.prod.yml
├── services
│   ├── web
│   │   ├── app.py
│   │   ├── requirements.txt
│   │   ├── templates
│   │   └── Dockerfile
│   ├── postgres
│   │   ├── schema.sql
│   │   └── Dockerfile
│   └── nginx
│       ├── nginx.conf
│       └── Dockerfile
└── .github
    └── workflows
        └── test.yml
```

---

# Full Text Search

This project uses PostgreSQL full-text search with:

- `to_tsvector`
- `plainto_tsquery`
- `ts_rank`
- `ts_headline`
- RUM indexes

---

# SQL Injection Prevention

All database queries use parameterized placeholders:

```python
cursor.execute(
    "SELECT * FROM users WHERE username=%s",
    (username,)
)
```

No f-string SQL queries are used.

---

# GitHub Actions

GitHub Actions automatically:

- builds containers
- starts containers
- verifies startup succeeds
