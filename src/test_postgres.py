import os
import sys

def get_conninfo():
    # Prefer DATABASE_URL if provided, otherwise build from individual vars
    url = os.getenv('DATABASE_URL')
    if url:
        return url
    user = os.getenv('PGUSER') or os.getenv('user') or os.getenv('USER')
    password = os.getenv('PGPASSWORD') or os.getenv('password')
    host = os.getenv('PGHOST') or os.getenv('host')
    port = os.getenv('PGPORT') or os.getenv('port')
    db = os.getenv('PGDATABASE') or os.getenv('database')
    if not (user and password and host and port and db):
        raise RuntimeError('Missing Postgres connection environment variables. Set DATABASE_URL or PGHOST/PGPORT/PGDATABASE/PGUSER/PGPASSWORD.')
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"

def main():
    try:
        import psycopg
    except Exception as e:
        print('psycopg is not installed or failed to import:', e)
        sys.exit(1)
    conninfo = get_conninfo()
    print('Connecting using:', conninfo if len(conninfo) < 80 else conninfo[:60] + '...')
    try:
        with psycopg.connect(conninfo) as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT version();')
                print('Postgres version:', cur.fetchone())
                cur.execute('SELECT count(*) FROM todos;')
                print('todos rows:', cur.fetchone())
    except Exception as e:
        print('Connection or query failed:', e)
        sys.exit(2)

if __name__ == '__main__':
    main()
