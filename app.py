from flask import Flask, request, jsonify, render_template_string
import psycopg2
from dotenv import load_dotenv
import os
from flask_cors import CORS
import sys

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def initialize_database():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Create table if it doesn't exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS links (
                id SERIAL PRIMARY KEY,
                url TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create index for better performance
        cur.execute("CREATE INDEX IF NOT EXISTS idx_url ON links(url)")
        
        conn.commit()
        print("Database initialized successfully", file=sys.stderr)
    except Exception as e:
        print(f"Database initialization failed: {e}", file=sys.stderr)
        raise e
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

# Initialize database when starting the app
initialize_database()

@app.route('/store', methods=['POST'])
def store_links():
    data = request.get_json()
    links = data.get('links', [])

    if not links:
        return jsonify({'error': 'No links provided'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        inserted_count = 0
        for link in links:
            try:
                # Use ON CONFLICT DO NOTHING to avoid duplicates
                cur.execute(
                    "INSERT INTO links (url) VALUES (%s) ON CONFLICT (url) DO NOTHING",
                    (link,)
                )
                if cur.rowcount > 0:
                    inserted_count += 1
            except Exception as e:
                print(f"Error inserting link {link}: {e}", file=sys.stderr)
        
        conn.commit()
        return jsonify({
            'status': 'success',
            'total_received': len(links),
            'inserted': inserted_count,
            'duplicates': len(links) - inserted_count
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

@app.route('/')
def index():
    return '''
    <h2>Flask WebM Collector</h2>
    <p><a href="/links">View Stored Links</a></p>
    <p>Send POST requests to /store with JSON containing "links" array</p>
    '''

@app.route('/links')
def show_links():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT url, created_at 
            FROM links 
            ORDER BY created_at DESC
            LIMIT 100
        """)
        links = cur.fetchall()
        
        html = '''
        <h2>Stored WebM Links (Newest First)</h2>
        <p>Total: {{ count }}</p>
        <ul>
          {% for link in links %}
            <li>
              <a href="{{ link[0] }}" target="_blank">{{ link[0] }}</a>
              <small>({{ link[1] }})</small>
            </li>
          {% endfor %}
        </ul>
        '''
        return render_template_string(html, links=links, count=len(links))
        
    except Exception as e:
        return f"<h2>Error</h2><p>{e}</p>"
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
