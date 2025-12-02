import os
import sqlite3

from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import contextmanager

print("=== 雲端版：使用 SQLite 啟動 FastAPI（不再使用 Oracle Client） ===")

app = FastAPI(title="User CRUD System (Cloud / SQLite)")

# === CORS 設定（保持不動）===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === 靜態檔案（保持不動）===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "static")),
    name="static",
)

# === 資料庫連線（SQLite 版，替代 Oracle）===
DB_PATH = os.path.join(BASE_DIR, "fastapi.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# === 初始化資料表（SQLite 版）===
def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # SQLite：自動遞增 PRIMARY KEY
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users_fastapi (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            name  TEXT,
            email TEXT
        )
        """
    )

    conn.commit()
    cur.close()
    conn.close()


@app.get("/", response_class=HTMLResponse)
def root():
    # ⚠️ 這段完全照你原本的，沒改
    with open(
        os.path.join(BASE_DIR, "static", "index.html"),
        "r",
        encoding="utf-8",
    ) as f:
        return f.read()


@app.get("/users/")
def get_users():
    # ⚠️ 這段也只把 Oracle 換成 SQLite，其它結構不動
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email FROM users_fastapi ORDER BY id")
    rows = cur.fetchall()
    data = [{"id": r["id"], "name": r["name"], "email": r["email"]} for r in rows]
    cur.close()
    conn.close()
    return data


# 🔻 把你「原本 main.py 裡的其它 CRUD（新增/修改/刪除/搜尋）」原封不動貼到這裡 🔻
# （只要裡面有用到 get_connection()，會自動改用 SQLite，不需要再改別的）
# 例如：
#
# @app.post("/users/")
# def create_user(name: str = Form(...), email: str = Form(...)):
#     conn = get_connection()
#     cur = conn.cursor()
#     cur.execute(
#         "INSERT INTO users_fastapi (name, email) VALUES (?, ?)",
#         (name, email),
#     )
#     conn.commit()
#     cur.close()
#     conn.close()
#     return {"message": "ok"}
#
# ... 之類，照你自己原本的邏輯即可
# 🔺🔺🔺


# === 啟動 ===
# Railway / 雲端其實會用 `main:app` 直接啟動，
# 這段只在你本機用 `python main.py` 測試時會跑，保留不動即可。
if __name__ == "__main__":
    init_db()
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
