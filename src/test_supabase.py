from supabase_client import get_supabase_client

def main():
    sb = get_supabase_client()
    # Sample call: try to select from a 'todos' table if exists
    try:
        res = sb.table('todos').select('*').execute()
        print('Status:', res.status_code if hasattr(res, 'status_code') else 'ok')
        print(res.data if hasattr(res, 'data') else res)
    except Exception as e:
        print('Error while querying Supabase:', e)

if __name__ == '__main__':
    main()
