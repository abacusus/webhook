from flask import Flask, request, jsonify, render_template_string
import psycopg2
from dotenv import load_dotenv
import os
from flask_cors import CORS

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

@app.route('/store', methods=['POST'])
def store_links():
    data = request.get_json()
    links = data.get('links', [])

    if not links:
        return jsonify({'error': 'No links provided'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        for link in links:
            cur.execute("INSERT INTO links (url) VALUES (%s)", (link,))
        
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'status': 'success', 'inserted': len(links)})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    return '''
    <h2>Flask App Running!</h2>
    <p><a href="/links">View Stored Links</a></p>
    '''

@app.route('/links')
def show_links():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT url FROM links ORDER BY id DESC")
        links = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        return f"<p>Error: {e}</p>"

    html = '''
    <h2>Stored Links</h2>
    <ul>
      {% for link in links %}
        <li><a href="{{ link[0] }}" target="_blank">{{ link[0] }}</a></li>
      {% endfor %}
    </ul>
    '''

    return render_template_string(html, links=links)

if __name__ == '__main__':
    app.run(debug=True)
