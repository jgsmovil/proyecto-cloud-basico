import os
import socket
import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)

def get_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        dbname=os.getenv("DB_NAME", "notasdb"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
    )

def init_db():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "CREATE TABLE IF NOT EXISTS notas (id SERIAL PRIMARY KEY, texto TEXT NOT NULL);"
            )

@app.route("/")
def home():
    return jsonify({
        "servicio": "API Notas Cloud",
        "entorno": os.getenv("APP_ENV", "desarrollo"),
        "replica_id": socket.gethostname()
    })

@app.route("/notas", methods=["GET", "POST"])
def notas():
    init_db()
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        texto = data.get("texto", "Nota de prueba")
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO notas (texto) VALUES (%s);", (texto,))
        return jsonify({"estado": "guardado", "replica_id": socket.gethostname()}), 201

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, texto FROM notas ORDER BY id DESC LIMIT 10;")
            filas = [{"id": r[0], "texto": r[1]} for r in cur.fetchall()]
    return jsonify({"replica_id": socket.gethostname(), "notas": filas})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)