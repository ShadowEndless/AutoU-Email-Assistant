import sqlite3
from datetime import datetime

DB_PATH = "classificacoes.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS classificacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conteudo TEXT NOT NULL,
            tipo TEXT NOT NULL,
            subtipo TEXT,
            data_hora TEXT NOT NULL,
            confianca REAL,
            remetente TEXT,
            assunto TEXT
        )
    """)
    conn.commit()
    conn.close()

def salvar_classificacao(conteudo, tipo, subtipo=None, confianca=None, remetente=None, assunto=None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO classificacoes (conteudo, tipo, subtipo, data_hora, confianca, remetente, assunto)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        conteudo,
        tipo,
        subtipo,
        datetime.now().isoformat(),
        confianca,
        remetente if remetente else None,
        assunto if assunto else None
    ))
    conn.commit()
    conn.close()

def listar_classificacoes(limit=50):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM classificacoes ORDER BY id DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()

    return [
        {
            "id": r[0],
            "conteudo": r[1],
            "tipo": r[2],
            "subtipo": r[3],
            "data_hora": r[4],
            "confianca": r[5],
            "remetente": r[6],
            "assunto": r[7]
        }
        for r in rows
    ]
