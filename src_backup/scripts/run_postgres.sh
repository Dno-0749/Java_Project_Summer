#!/bin/bash

# Function to check if PostgreSQL is running
is_postgres_running() {
    pg_isready -q
    return $?
}

# Start PostgreSQL if it's not already running
if ! is_postgres_running; then
    echo "PostgreSQL is not running. Starting it now..."
    pg_ctl -D /usr/local/var/postgres -l /usr/local/var/postgres/server.log start
else
    echo "PostgreSQL is already running."
fi

# Create the database if it doesn't exist
if ! psql -lqt | cut -d \| -f 1 | grep -qw dbname; then
    createdb dbname
fi
