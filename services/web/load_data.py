#!/usr/bin/env python3
"""
load_data.py — loads twitter data into the messages/users tables.

Usage (run inside the web container):
    # Load from twitter_parallel files (small, for dev):
    python load_data.py --source /data/twitter_parsed_reduced

    # Load from twitter_indexes files (full 1M+ rows, for prod):
    python load_data.py --source /data/twitter_parsed

The expected input directory should contain:
    users.csv   — columns: id_users, username
    tweets.csv  — columns: id_tweets, id_users, created_at, text

If you don't have the course data files, run with --generate
to create synthetic test data instead:
    python load_data.py --generate --users 1000 --messages 10000
"""

import os
import csv
import argparse
import random
import string
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import execute_values
from werkzeug.security import generate_password_hash


DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://hello_flask:hello_flask@db:5432/hello_flask_dev')
BATCH_SIZE   = 10_000  # rows per INSERT batch


def get_conn():
    return psycopg2.connect(DATABASE_URL)


# ---------------------------------------------------------------------------
# Load from course CSV files
# ---------------------------------------------------------------------------

def load_from_files(source_dir: str):
    conn = get_conn()
    cur  = conn.cursor()

    print(f'Loading users from {source_dir}/users.csv ...')
    users_loaded = 0
    with open(os.path.join(source_dir, 'users.csv'), 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        batch  = []
        for row in reader:
            batch.append((row['id_users'], row['username']))
            if len(batch) >= BATCH_SIZE:
                execute_values(cur, '''
                    INSERT INTO users (id_users, username)
                    VALUES %s
                    ON CONFLICT DO NOTHING
                ''', batch)
                conn.commit()
                users_loaded += len(batch)
                print(f'  {users_loaded:,} users loaded...')
                batch = []
        if batch:
            execute_values(cur, '''
                INSERT INTO users (id_users, username)
                VALUES %s
                ON CONFLICT DO NOTHING
            ''', batch)
            conn.commit()
            users_loaded += len(batch)

    print(f'Users loaded: {users_loaded:,}')

    print(f'Loading messages from {source_dir}/tweets.csv ...')
    messages_loaded = 0
    with open(os.path.join(source_dir, 'tweets.csv'), 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        batch  = []
        for row in reader:
            # Adapt column names to your CSV format
            id_users   = row.get('id_users')
            message    = row.get('text') or row.get('tweet') or row.get('message', '')
            created_at = row.get('created_at', None)
            batch.append((id_users, message[:280], created_at))
            if len(batch) >= BATCH_SIZE:
                execute_values(cur, '''
                    INSERT INTO messages (id_users, message, created_at)
                    VALUES %s
                    ON CONFLICT DO NOTHING
                ''', batch)
                conn.commit()
                messages_loaded += len(batch)
                print(f'  {messages_loaded:,} messages loaded...')
                batch = []
        if batch:
            execute_values(cur, '''
                INSERT INTO messages (id_users, message, created_at)
                VALUES %s
                ON CONFLICT DO NOTHING
            ''', batch)
            conn.commit()
            messages_loaded += len(batch)

    print(f'Messages loaded: {messages_loaded:,}')
    cur.close()
    conn.close()


# ---------------------------------------------------------------------------
# Generate synthetic test data (no course files needed)
# ---------------------------------------------------------------------------

SAMPLE_WORDS = [
    'python', 'flask', 'postgres', 'database', 'docker', 'nginx', 'gunicorn',
    'index', 'query', 'rum', 'gin', 'search', 'fulltext', 'tweet', 'message',
    'hello', 'world', 'love', 'great', 'awesome', 'bad', 'good', 'today',
    'tomorrow', 'yesterday', 'morning', 'night', 'coffee', 'code', 'bug',
    'feature', 'deploy', 'server', 'cloud', 'api', 'web', 'app', 'data',
    'machine', 'learning', 'neural', 'network', 'claremont', 'mckenna', 'college',
]


def random_message():
    length = random.randint(5, 30)
    return ' '.join(random.choices(SAMPLE_WORDS, k=length))


def random_username(n):
    return 'user_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6)) + str(n)


def generate_data(num_users: int, num_messages: int):
    conn = get_conn()
    cur  = conn.cursor()

    print(f'Generating {num_users:,} users...')
    user_ids = []
    user_batch = []
    for i in range(num_users):
        username = random_username(i)
        user_batch.append((username,))
        if len(user_batch) >= BATCH_SIZE:
            execute_values(cur, '''
                INSERT INTO users (username) VALUES %s
                RETURNING id_users
            ''', user_batch)
            rows = cur.fetchall()
            user_ids.extend(r[0] for r in rows)
            conn.commit()
            print(f'  {len(user_ids):,} users inserted...')
            user_batch = []

    if user_batch:
        execute_values(cur, 'INSERT INTO users (username) VALUES %s RETURNING id_users', user_batch)
        rows = cur.fetchall()
        user_ids.extend(r[0] for r in rows)
        conn.commit()

    print(f'Users generated: {len(user_ids):,}')

    # Add a default hashed password for every user (for testing login)
    print('Adding credentials for all users...')
    hashed = generate_password_hash('password123')
    cred_batch = [(uid, hashed) for uid in user_ids]
    for i in range(0, len(cred_batch), BATCH_SIZE):
        execute_values(cur, 'INSERT INTO credentials (id_users, password) VALUES %s', cred_batch[i:i+BATCH_SIZE])
        conn.commit()

    print(f'Generating {num_messages:,} messages...')
    base_time = datetime.utcnow() - timedelta(days=365)
    msg_batch = []
    total     = 0
    for i in range(num_messages):
        uid        = random.choice(user_ids)
        msg        = random_message()
        created_at = base_time + timedelta(seconds=random.randint(0, 365*24*3600))
        msg_batch.append((uid, msg, created_at))
        if len(msg_batch) >= BATCH_SIZE:
            execute_values(cur, '''
                INSERT INTO messages (id_users, message, created_at) VALUES %s
            ''', msg_batch)
            conn.commit()
            total += len(msg_batch)
            print(f'  {total:,} messages inserted...')
            msg_batch = []

    if msg_batch:
        execute_values(cur, 'INSERT INTO messages (id_users, message, created_at) VALUES %s', msg_batch)
        conn.commit()
        total += len(msg_batch)

    print(f'Messages generated: {total:,}')
    cur.close()
    conn.close()
    print('Done! All data loaded.')


# ---------------------------------------------------------------------------

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Load data into the twitter clone database')
    parser.add_argument('--source',   type=str, help='Directory with users.csv and tweets.csv')
    parser.add_argument('--generate', action='store_true', help='Generate synthetic data instead')
    parser.add_argument('--users',    type=int, default=1_000_000,   help='Number of synthetic users')
    parser.add_argument('--messages', type=int, default=1_000_000, help='Number of synthetic messages')
    args = parser.parse_args()

    if args.generate:
        generate_data(args.users, args.messages)
    elif args.source:
        load_from_files(args.source)
    else:
        print('Specify --source <dir> to load from CSV files, or --generate to create synthetic data.')
        parser.print_help()

