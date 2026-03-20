from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2
import os

app = Flask(__name__)
CORS(app)  # Tillåter anrop från din Vue-frontend (port 8080)

def get_db_connection():
    """Skapar en koppling till Postgres-containern."""
    conn = psycopg2.connect(
        host="db",           # Måste matcha servicenamnet i docker-compose.yml
        database="shopping_db",
        user="user",
        password="pass"
    )
    return conn

def init_db():
    """Skapar tabellen om den inte redan finns vid start."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS shoppinglist (
                id SERIAL PRIMARY KEY,
                item TEXT NOT NULL,
                category TEXT,
                purchased BOOLEAN DEFAULT FALSE
            );
        ''')
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Databasen är initierad och tabellen 'shoppinglist' är redo.")
    except Exception as e:
        print(f"❌ Fel vid initiering av databas: {e}")

@app.route('/api/items', methods=['GET'])
def get_items():
    """Hämtar alla varor från databasen."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Vi hämtar 4 kolumner: id(0), item(1), category(2), purchased(3)
        cur.execute('SELECT id, item, category, purchased FROM shoppinglist;')
        items = cur.fetchall()
        cur.close()
        conn.close()

        # Omvandlar datan till en lista med JSON-objekt
        return jsonify([{
            "id": i[0], 
            "item": i[1], 
            "category": i[2], 
            "purchased": i[3]
        } for i in items])
    except Exception as e:
        print(f"DEBUG ERROR: {e}")
        return jsonify({"error": str(e)}), 500

# STARTPUNKT
if __name__ == '__main__':
    # 1. Förbered databasen innan servern startar
    with app.app_context():
        init_db()
    
    # 2. Starta Flask-servern
    # host='0.0.0.0' krävs för att nå den utanför containern
    print("🚀 Startar Flask-servern på port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=True)