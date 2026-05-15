# Twitter Final Project

[![Tests](https://github.com/Jessiek37185/twitter_final/actions/workflows/test.yml/badge.svg)](https://github.com/Jessiek37185/twitter_final/actions)

A Dockerized Twitter-style social media web application built with Flask and PostgreSQL. The application supports user authentication, message posting, full-text search, ranked search results, highlighted search matches, pagination, and scalable database indexing using PostgreSQL RUM indexes.

This project was designed to handle large datasets efficiently while preventing SQL injection vulnerabilities and ensuring all routes remain stable under malformed input and invalid requests.

---

# Features

## User Authentication
- Create accounts
- Login/logout functionality
- Password confirmation during registration
- Password hashing using Werkzeug security utilities
- Session-based authentication

---

## Message Feed
- Homepage displays all messages in the system
- Messages ordered chronologically (newest first)
- Displays:
  - username
  - timestamp
  - message contents
- Pagination support (20 messages per page)

---

## Message Creation
- Logged-in users can create posts
- Stores:
  - user id
  - creation timestamp
  - message contents
- Newly created messages immediately appear on homepage

---

## Full-Text Search
- PostgreSQL Full-Text Search (FTS)
- Ranked search results using `ts_rank`
- Highlighted search matches using `ts_headline`
- Pagination support for search results
- Uses PostgreSQL RUM indexes instead of GIN indexes for faster ranked search queries

---

## Extra Credit Features
- Spelling suggestions using `pg_trgm`
- Trigram similarity matching for misspelled words

---

## Security Features
- SQL injection prevention using parameterized queries
- Safe handling of malformed search queries
- Input validation on login and registration routes
- Protected session handling
- Custom error handling for invalid routes and server errors

---

# Technologies Used

| Technology | Purpose |
|---|---|
| Flask | Web framework |
| PostgreSQL | Relational database |
| Docker | Containerization |
| Docker Compose | Multi-container orchestration |
| GitHub Actions | Automated CI testing |
| psycopg2 | PostgreSQL database adapter |
| PostgreSQL FTS | Full-text search |
| RUM indexes | Fast ranked search |
| pg_trgm | Spelling suggestions |

---

# Project Structure

```text
twitter_final/
├── .github/
│   └── workflows/
│       └── test.yml
├── services/
│   ├── postgres/
│   │   ├── Dockerfile
│   │   └── schema.sql
│   ├── web/
│   │   ├── app.py
│   │   ├── load_data.py
│   │   ├── requirements.txt
│   │   ├── Dockerfile
│   │   └── templates/
│   └── nginx/
│       ├── Dockerfile
│       └── nginx.conf
├── tests/
│   └── login.sh
├── docker-compose.yml
├── docker-compose.prod.yml
├── README.md
└── .env.dev
```

---

# Database Schema

The database schema is located at:

```text
services/postgres/schema.sql
```

The schema automatically loads when the PostgreSQL container starts.

The project uses three main tables:

---

## users

Stores user account information.

| Column | Type | Constraints |
|---|---|---|
| id_users | BIGSERIAL | PRIMARY KEY |
| username | TEXT | UNIQUE, NOT NULL |
| created_at | TIMESTAMPTZ | DEFAULT NOW() |

Indexes:
- `idx_users_username`

---

## credentials

Stores user passwords separately from account information for security purposes.

| Column | Type | Constraints |
|---|---|---|
| id_credentials | BIGSERIAL | PRIMARY KEY |
| id_users | BIGINT | FOREIGN KEY REFERENCES users(id_users) |
| password | TEXT | NOT NULL |

Indexes:
- `idx_credentials_id_users`

---

## messages

Stores all tweet-style posts/messages.

| Column | Type | Constraints |
|---|---|---|
| id_messages | BIGSERIAL | PRIMARY KEY |
| id_users | BIGINT | FOREIGN KEY REFERENCES users(id_users) |
| message | TEXT | NOT NULL |
| created_at | TIMESTAMPTZ | DEFAULT NOW() |

Indexes:
- `idx_messages_created_at`
- `idx_messages_id_users`
- `idx_messages_rum`
- `idx_messages_trgm`

---

# Database Relationships

```text
users
  |
  |---< credentials
  |
  |---< messages
```

- One user has one credential record
- One user can create many messages
- Messages are linked to users through `id_users`

---

# PostgreSQL Extensions

The schema enables the following PostgreSQL extensions:

| Extension | Purpose |
|---|---|
| `rum` | Fast ranked full-text search |
| `pg_trgm` | Spelling suggestions and trigram similarity |

---

# Full-Text Search

The `/search` route uses PostgreSQL Full-Text Search (FTS) with:

- `to_tsvector`
- `plainto_tsquery`
- `ts_rank`
- `ts_headline`

The project uses a RUM index instead of a GIN index to improve ranked search performance.

Example search query structure:

```sql
SELECT
    u.username,
    ts_headline(...),
    ts_rank(...)
FROM messages m
JOIN users u ON m.id_users = u.id_users
WHERE to_tsvector('english', m.message)
      @@ plainto_tsquery('english', %s)
ORDER BY rank DESC;
```

---

# Routes

## `/`
Homepage route displaying all messages.

Features:
- visible whether logged in or logged out
- chronological ordering
- pagination
- indexed query performance

---

## `/login`
User authentication route.

Features:
- hidden password field
- invalid login protection
- redirect after successful login

---

## `/logout`
Clears session cookies and logs out the user.

---

## `/create_account`
Account registration route.

Features:
- duplicate username prevention
- password confirmation validation
- hashed password storage

---

## `/create_message`
Allows logged-in users to create messages.

---

## `/search`
Full-text search route.

Features:
- ranked results
- highlighted matches
- pagination
- spelling suggestions

---

# Performance Optimization

The project is designed to support large datasets efficiently.

Optimizations include:
- indexed chronological sorting
- RUM full-text indexes
- trigram indexes
- paginated queries using `LIMIT` and `OFFSET`
- parameterized SQL queries

The project supports:
- 1,000,000+ rows in multiple tables
- scalable search performance

---

# Loading Test Data

The project includes a data loading utility:

```text
services/web/load_data.py
```

This script can:
- generate synthetic data
- load course datasets
- bulk insert large amounts of rows efficiently

Example:

```bash
docker compose exec web python load_data.py --generate --users 1000000 --messages 1000000
```

---

# Development Setup

## Clone repository

```bash
git clone https://github.com/Jessiek37185/twitter_final.git
cd twitter_final
```

---

## Create environment file

Create:

```text
.env.dev
```

Contents:

```text
DATABASE_URL=postgresql://hello_flask:hello_flask@db:5432/hello_flask_dev
SECRET_KEY=supersecret
```

---

## Start containers

```bash
docker compose up --build
```

---

## Open application

Local machine:

```text
http://localhost:9898
```

Lambda server:

```text
http://lambda.compute.cmc.edu:9898
```

---

# Automated Testing

GitHub Actions automatically:
- builds containers
- starts containers
- verifies container startup
- runs login tests

Workflow file:

```text
.github/workflows/test.yml
```

---

# Login Testing

The project includes automated login tests:

```text
tests/login.sh
```

The test script validates:
- homepage accessibility
- login route accessibility
- invalid login handling
- SQL injection resistance
- absence of Flask tracebacks

Run locally:

```bash
./tests/login.sh
```

---

# SQL Injection Prevention

All database queries use parameterized SQL queries.

Example:

```python
cur.execute(
    "SELECT * FROM users WHERE username = %s",
    (username,)
)
```

The application safely handles malicious inputs such as:

```text
' OR 1=1 --
```

without exposing database errors or bypassing authentication.

---

# Error Handling

The application includes:
- flash error messages
- invalid login handling
- malformed search query handling
- custom 404 pages
- custom 500 pages

This prevents routes from crashing during invalid requests.

