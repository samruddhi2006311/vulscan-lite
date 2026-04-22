import psycopg2
import psycopg2.extras
import os
import json
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    """Create a new database connection with SSL"""
    conn = psycopg2.connect(
        DATABASE_URL,
        sslmode='require'
    )
    return conn


def save_scan(job_id, result):
    """Save a completed scan to database"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO scan_history (
                url, grade, score, job_id,
                ssl_valid, ssl_days_left, cms_name,
                headers_passed, headers_failed
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            result.get('url', ''),
            result.get('grade', ''),
            result.get('total_score', 0),
            job_id,
            result.get('ssl', {}).get('is_valid', False),
            result.get('ssl', {}).get('days_left'),
            result.get('cms', {}).get('cms_name'),
            json.dumps(result.get('headers', {}).get('passed', [])),
            json.dumps(result.get('headers', {}).get('failed', []))
        ))
        conn.commit()
        print(f"✅ Scan saved to database: {result.get('url')}")
    except Exception as e:
        conn.rollback()
        print(f"❌ Database save error: {e}")
        raise e
    finally:
        cursor.close()
        conn.close()


def get_history(limit=50):
    """Get all scan history newest first"""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cursor.execute('''
            SELECT * FROM scan_history
            ORDER BY scanned_at DESC
            LIMIT %s
        ''', (limit,))
        rows = cursor.fetchall()

        history = []
        for row in rows:
            history.append({
                'id': row['id'],
                'url': row['url'],
                'grade': row['grade'],
                'score': row['score'],
                'job_id': row['job_id'],
                'ssl_valid': row['ssl_valid'],
                'ssl_days_left': row['ssl_days_left'],
                'cms_name': row['cms_name'],
                'headers_passed': row['headers_passed'] or [],
                'headers_failed': row['headers_failed'] or [],
                'scanned_at': str(row['scanned_at'])[:16].replace('T', ' ')
            })
        return history
    except Exception as e:
        print(f"❌ Database fetch error: {e}")
        raise e
    finally:
        cursor.close()
        conn.close()


def delete_history():
    """Clear all scan history"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM scan_history')
        conn.commit()
        print("✅ History cleared")
    except Exception as e:
        conn.rollback()
        print(f"❌ Database delete error: {e}")
        raise e
    finally:
        cursor.close()
        conn.close()