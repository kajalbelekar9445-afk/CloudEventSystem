from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "campus-events-secret-key"

def create_database():
    conn = sqlite3.connect("events.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            department TEXT NOT NULL,
            event TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

create_database()

@app.route("/")
def home():
    return render_template("index.html")
@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if username == "admin" and password == "admin123":
            session["admin_logged_in"] = True
            return redirect(url_for("admin"))

        return render_template(
            "admin_login.html",
            error="Invalid username or password!"
        )

    return render_template("admin_login.html")


@app.route("/admin-logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin_login"))
@app.route("/admin")
def admin():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))
    conn = sqlite3.connect("events.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM registrations ORDER BY id DESC"
    )
    registrations = cursor.fetchall()

    conn.close()

    return render_template(
        "admin.html",
        registrations=registrations
    )

@app.route("/register", methods=["POST"])
def register():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    department = request.form.get("department", "").strip()
    event = request.form.get("event", "").strip()

    if not all([name, email, department, event]):
        return "Please fill in all fields.", 400

    conn = sqlite3.connect("events.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO registrations (name, email, department, event)
        VALUES (?, ?, ?, ?)
    """, (name, email, department, event))

    conn.commit()
    conn.close()

    return render_template(
        "success.html",
        name=name,
        event=event
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)