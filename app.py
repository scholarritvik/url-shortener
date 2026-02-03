from flask import Flask, render_template, request, redirect, url_for
import random
import string
import sqlite3

app = Flask(__name__)

url_db = {}  # temporary storage

def init_db():
    conn = sqlite3.connect("urls.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE,
            original_url TEXT,
            clicks INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

init_db()

def generate(length=6):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        original_url = request.form["url"]
        code = generate()

        conn = sqlite3.connect("urls.db")
        c = conn.cursor()
        c.execute("INSERT INTO urls (code, original_url) VALUES (?, ?)", (code, original_url))
        conn.commit()
        conn.close()

        return redirect(url_for("result", code=code))

    return render_template("index.html")


@app.route("/result/<code>")
def result(code):
    short_url = url_for("redirect_url", code=code, _external=True)
    return render_template("index.html", short_url=short_url)


@app.route("/<code>")
def redirect_url(code):
    conn = sqlite3.connect("urls.db")
    c = conn.cursor()

    c.execute("SELECT original_url, clicks FROM urls WHERE code=?", (code,))
    row = c.fetchone()

    if row:
        original_url, clicks = row
        c.execute("UPDATE urls SET clicks=? WHERE code=?", (clicks+1, code))
        conn.commit()
        conn.close()
        return redirect(original_url)

    conn.close()
    return "URL not found!"

@app.route("/stats")
def stats():
    conn = sqlite3.connect("urls.db")
    c = conn.cursor()

    c.execute("SELECT code, original_url, clicks FROM urls")
    data = c.fetchall()

    conn.close()

    return render_template("stats.html",data=data)


if __name__ == "__main__":
    app.run(debug=True)
