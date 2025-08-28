import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Try to import psycopg2 at module level
try:
    import psycopg2
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

def get_db_connection():
    """Get database connection"""
    database_url = os.getenv('RENDER_DB_KEY')
    if database_url and PSYCOPG2_AVAILABLE:
        try:
            return psycopg2.connect(database_url)
        except Exception as e:
            print(f"Warning: PostgreSQL connection failed: {e}, falling back to SQLite")
            import sqlite3
            return sqlite3.connect('sbc_records.db')
    else:
        # Fallback to local SQLite for development
        if database_url and not PSYCOPG2_AVAILABLE:
            print("Warning: psycopg2 not available, falling back to SQLite")
        import sqlite3
        return sqlite3.connect('sbc_records.db')

def init_db():
    """Initialize the database and create tables if they don't exist"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if we're using PostgreSQL or SQLite
    if PSYCOPG2_AVAILABLE and isinstance(conn, psycopg2.extensions.connection):
        # PostgreSQL
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sbc_records (
                id SERIAL PRIMARY KEY,
                group_name VARCHAR(255) NOT NULL,
                upload_date VARCHAR(10) NOT NULL,
                penalty_a VARCHAR(10) NOT NULL,
                penalty_b VARCHAR(10) NOT NULL,
                filename VARCHAR(255) NOT NULL,
                s3_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    else:
        # SQLite
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sbc_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_name TEXT NOT NULL,
                upload_date TEXT NOT NULL,
                penalty_a TEXT NOT NULL,
                penalty_b TEXT NOT NULL,
                filename TEXT NOT NULL,
                s3_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    conn.commit()
    conn.close()

def insert_record(group_name, penalty_a, penalty_b, filename, s3_url=None):
    """Insert a new SBC record into the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    upload_date = datetime.now().strftime('%Y-%m-%d')
    
    cursor.execute('''
        INSERT INTO sbc_records (group_name, upload_date, penalty_a, penalty_b, filename, s3_url)
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', (group_name, upload_date, penalty_a, penalty_b, filename, s3_url))
    
    conn.commit()
    conn.close()

def get_all_records():
    """Retrieve all SBC records from the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, group_name, upload_date, penalty_a, penalty_b, filename, s3_url, created_at
        FROM sbc_records
        ORDER BY created_at DESC
    ''')
    
    records = cursor.fetchall()
    conn.close()
    
    # Convert to list of dictionaries for JSON serialization
    formatted_records = []
    for record in records:
        # PostgreSQL/SQLite returns: (id, group_name, upload_date, penalty_a, penalty_b, filename, s3_url, created_at)
        formatted_records.append({
            'id': record[0],
            'group_name': record[1],
            'upload_date': record[2],
            'penalty_a': record[3],
            'penalty_b': record[4],
            'filename': record[5],
            's3_url': record[6],
            'created_at': record[7] if len(record) > 7 else None
        })
    
    return formatted_records

def get_record_by_id(record_id):
    """Get a record by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, group_name, upload_date, penalty_a, penalty_b, filename, s3_url, created_at
        FROM sbc_records WHERE id = %s
    ''', (record_id,))
    
    record = cursor.fetchone()
    conn.close()
    
    if record:
        return {
            'id': record[0],
            'group_name': record[1],
            'upload_date': record[2],
            'penalty_a': record[3],
            'penalty_b': record[4],
            'filename': record[5],
            's3_url': record[6],
            'created_at': record[7] if len(record) > 7 else None
        }
    return None

def delete_record(record_id):
    """Delete a record by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM sbc_records WHERE id = %s', (record_id,))
    
    conn.commit()
    conn.close()
