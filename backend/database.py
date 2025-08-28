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
    print(f"Database URL available: {database_url is not None}")
    print(f"PSYCOPG2_AVAILABLE: {PSYCOPG2_AVAILABLE}")
    
    if database_url and PSYCOPG2_AVAILABLE:
        try:
            conn = psycopg2.connect(database_url)
            print("Connected to PostgreSQL database")
            return conn
        except Exception as e:
            print(f"Warning: PostgreSQL connection failed: {e}, falling back to SQLite")
            import sqlite3
            return sqlite3.connect('sbc_records.db')
    else:
        # Fallback to local SQLite for development
        if database_url and not PSYCOPG2_AVAILABLE:
            print("Warning: psycopg2 not available, falling back to SQLite")
        import sqlite3
        print("Using SQLite database")
        return sqlite3.connect('sbc_records.db')

def init_db():
    """Initialize the database and create tables if they don't exist"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if we're using PostgreSQL or SQLite
        if PSYCOPG2_AVAILABLE and isinstance(conn, psycopg2.extensions.connection):
            # PostgreSQL
            print("Initializing PostgreSQL database")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sbc_records (
                    id SERIAL PRIMARY KEY,
                    group_name VARCHAR(255) NOT NULL,
                    upload_date VARCHAR(10) NOT NULL,
                    penalty_a VARCHAR(10) NOT NULL,
                    penalty_b VARCHAR(10) NOT NULL,
                    filename VARCHAR(255) NOT NULL,
                    s3_url TEXT,
                    penalty_a_explanation TEXT,
                    penalty_b_explanation TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Add explanation columns to existing table if they don't exist
            try:
                cursor.execute('ALTER TABLE sbc_records ADD COLUMN penalty_a_explanation TEXT')
            except Exception as e:
                print(f"Column penalty_a_explanation may already exist: {e}")
                
            try:
                cursor.execute('ALTER TABLE sbc_records ADD COLUMN penalty_b_explanation TEXT')
            except Exception as e:
                print(f"Column penalty_b_explanation may already exist: {e}")

        else:
            # SQLite
            print("Initializing SQLite database")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sbc_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_name TEXT NOT NULL,
                    upload_date TEXT NOT NULL,
                    penalty_a TEXT NOT NULL,
                    penalty_b TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    s3_url TEXT,
                    penalty_a_explanation TEXT,
                    penalty_b_explanation TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # For SQLite, add columns if they don't exist
            try:
                cursor.execute('ALTER TABLE sbc_records ADD COLUMN penalty_a_explanation TEXT')
            except Exception as e:
                print(f"Column penalty_a_explanation may already exist: {e}")
                
            try:
                cursor.execute('ALTER TABLE sbc_records ADD COLUMN penalty_b_explanation TEXT')
            except Exception as e:
                print(f"Column penalty_b_explanation may already exist: {e}")
        
        conn.commit()
        conn.close()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
        if 'conn' in locals():
            conn.close()
        raise

def insert_record(group_name, penalty_a, penalty_b, filename, s3_url=None,
                 penalty_a_explanation=None, penalty_b_explanation=None):
    """Insert a new SBC record into the database with explanations"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        upload_date = datetime.now().strftime('%Y-%m-%d')
        
        # Check if we're using PostgreSQL or SQLite and use appropriate placeholders
        if PSYCOPG2_AVAILABLE and isinstance(conn, psycopg2.extensions.connection):
            # PostgreSQL
            print("Using PostgreSQL placeholders (%s)")
            cursor.execute('''
                INSERT INTO sbc_records 
                (group_name, upload_date, penalty_a, penalty_b, filename, s3_url, 
                 penalty_a_explanation, penalty_b_explanation)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (group_name, upload_date, penalty_a, penalty_b, filename, s3_url,
                  penalty_a_explanation, penalty_b_explanation))
        else:
            # SQLite
            print("Using SQLite placeholders (?)")
            cursor.execute('''
                INSERT INTO sbc_records 
                (group_name, upload_date, penalty_a, penalty_b, filename, s3_url,
                 penalty_a_explanation, penalty_b_explanation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (group_name, upload_date, penalty_a, penalty_b, filename, s3_url,
                  penalty_a_explanation, penalty_b_explanation))
        
        conn.commit()
        conn.close()
        print(f"Successfully inserted record for {group_name}")
    except Exception as e:
        print(f"Error inserting record: {e}")
        if 'conn' in locals():
            conn.close()
        raise

def get_all_records():
    """Retrieve all SBC records from the database including explanations"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, group_name, upload_date, penalty_a, penalty_b, filename, s3_url, 
               penalty_a_explanation, penalty_b_explanation, created_at
        FROM sbc_records
        ORDER BY created_at DESC
    ''')
    
    records = cursor.fetchall()
    conn.close()
    
    # Convert to list of dictionaries for JSON serialization
    formatted_records = []
    for record in records:
        formatted_records.append({
            'id': record[0],
            'group_name': record[1],
            'upload_date': record[2],
            'penalty_a': record[3],
            'penalty_b': record[4],
            'filename': record[5],
            's3_url': record[6],
            'penalty_a_explanation': record[7] if len(record) > 7 else '',
            'penalty_b_explanation': record[8] if len(record) > 8 else '',
            'created_at': record[9] if len(record) > 9 else None
        })
    
    return formatted_records

def get_record_by_id(record_id):
    """Get a record by ID including explanations"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if we're using PostgreSQL or SQLite and use appropriate placeholders
    if PSYCOPG2_AVAILABLE and isinstance(conn, psycopg2.extensions.connection):
        # PostgreSQL
        cursor.execute('''
            SELECT id, group_name, upload_date, penalty_a, penalty_b, filename, s3_url, 
                   penalty_a_explanation, penalty_b_explanation, created_at
            FROM sbc_records WHERE id = %s
        ''', (record_id,))
    else:
        # SQLite
        cursor.execute('''
            SELECT id, group_name, upload_date, penalty_a, penalty_b, filename, s3_url,
                   penalty_a_explanation, penalty_b_explanation, created_at
            FROM sbc_records WHERE id = ?
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
            'penalty_a_explanation': record[7] if len(record) > 7 else '',
            'penalty_b_explanation': record[8] if len(record) > 8 else '',
            'created_at': record[9] if len(record) > 9 else None
        }
    return None

def delete_record(record_id):
    """Delete a record by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if we're using PostgreSQL or SQLite and use appropriate placeholders
    if PSYCOPG2_AVAILABLE and isinstance(conn, psycopg2.extensions.connection):
        # PostgreSQL
        cursor.execute('DELETE FROM sbc_records WHERE id = %s', (record_id,))
    else:
        # SQLite
        cursor.execute('DELETE FROM sbc_records WHERE id = ?', (record_id,))
    
    conn.commit()
    conn.close()
