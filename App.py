from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2
import os

app = Flask(__name__)
CORS(app) # Tillåter din Vue-frontend att anropa backenden

def get_db_connection():
    conn = psycopg2.connect(
        host="db", # Namnet på tjänsten i docker-compose
        database="shopping_db",
        user="user",
        password="pass"
    )
    return conn

@app.route('/api/items', methods=['GET'])
def get_items():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT id, item, category, purchased FROM shoppinglist;')
        items = cur.fetchall()
        cur.close()
        conn.close()

        # Omvandla från tuple till lista med dicts
        return jsonify([{"id": i[0], "item": i[1], "purchased": i[2]} for i in items])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)