from flask import Flask, render_template, request, redirect
import pymssql
import os

app = Flask(__name__)

def get_conn():
    server = os.getenv("SQL_SERVER")
    database = os.getenv("SQL_DATABASE")
    username = os.getenv("SQL_USERNAME")
    password = os.getenv("SQL_PASSWORD")
    return pymssql.connect(server=server, user=username, password=password, database=database)

def init_db():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='tasks' AND xtype='U')
        CREATE TABLE tasks (
            id INT PRIMARY KEY IDENTITY(1,1),
            title NVARCHAR(100),
            done BIT
        )
    """)
    conn.commit()
    conn.close()

@app.route("/")
def index():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    conn.close()
    return render_template("index.html", tasks=tasks)

@app.route("/add", methods=["POST"])
def add_task():
    title = request.form.get("title")
    if title:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", (title, 0))
        conn.commit()
        conn.close()
    return redirect("/")

@app.route("/done/<int:task_id>")
def mark_done(task_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET done = 1 WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return redirect("/")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
