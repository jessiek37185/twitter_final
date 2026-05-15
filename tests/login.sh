#!/bin/bash

BASE_URL="http://localhost:9898"

echo "Testing homepage..."
curl -f $BASE_URL > /dev/null
if [ $? -ne 0 ]; then
    echo "Homepage failed"
    exit 1
fi

echo "Testing login page..."
curl -f $BASE_URL/login > /dev/null
if [ $? -ne 0 ]; then
    echo "Login page failed"
    exit 1
fi

echo "Testing SQL injection attempt..."

RESPONSE=$(curl -s -X POST \
    -d "username=' OR 1=1 --&password=test" \
    $BASE_URL/login)

echo "$RESPONSE" | grep -qi "traceback"
if [ $? -eq 0 ]; then
    echo "SQL injection caused traceback"
    exit 1
fi

echo "$RESPONSE" | grep -qi "psycopg2"
if [ $? -eq 0 ]; then
    echo "Database error exposed"
    exit 1
fi

echo "Testing invalid login..."

RESPONSE=$(curl -s -X POST \
    -d "username=fakeuser&password=fakepass" \
    $BASE_URL/login)

echo "$RESPONSE" | grep -qi "invalid"
if [ $? -ne 0 ]; then
    echo "Invalid login message missing"
    exit 1
fi

echo "All login tests passed!"
exit 0
