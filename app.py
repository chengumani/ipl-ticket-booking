from flask import Flask, render_template, request, redirect, flash, session
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = '1234'


# ---------- DATABASE CONNECTION ----------
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQLHOST"),
        user=os.getenv("MYSQLUSER"),
        password=os.getenv("MYSQLPASSWORD"),
        database=os.getenv("MYSQLDATABASE"),
        port=int(os.getenv("MYSQLPORT"))
    )


# ---------- HOME ----------
@app.route('/')
def index():
    return render_template('index.html')


# ---------- REGISTER ----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        conn = get_db_connection()
        cursor = conn.cursor()

        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        password = request.form['password']

        cursor.execute("SELECT * FROM user WHERE email = %s", (email,))
        if cursor.fetchone():
            flash("Email already registered.")
            cursor.close()
            conn.close()
            return redirect('/register')

        cursor.execute(
            "INSERT INTO user (name, phone, email, password) VALUES (%s, %s, %s, %s)",
            (name, phone, email, password)
        )
        conn.commit()

        cursor.close()
        conn.close()
        flash("Registered successfully.")
        return redirect('/login')

    return render_template('register.html')


# ---------- LOGIN ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        conn = get_db_connection()
        cursor = conn.cursor()

        email = request.form['email']
        password = request.form['password']

        cursor.execute(
            "SELECT * FROM user WHERE email = %s AND password = %s",
            (email, password)
        )
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            session['phone'] = user[2]
            session['email'] = user[3]
            return redirect('/dashboard')

        flash("Invalid credentials.")
        return redirect('/login')

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        return render_template('dashboard.html', username=session['user_name'])
    return redirect('/login')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# ---------- ADMIN ----------
ADMIN_EMAIL = 'admin@gmail.com'
ADMIN_PASSWORD = 'admin123'


@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['email'] == ADMIN_EMAIL and request.form['password'] == ADMIN_PASSWORD:
            session['admin'] = ADMIN_EMAIL
            return redirect('/admin_dashboard')
        flash("Invalid admin credentials")
        return redirect('/admin_login')

    return render_template('admin_login.html')


@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin' in session:
        return render_template('admin_dashboard.html')
    return redirect('/admin_login')


@app.route('/admin_logout')
def admin_logout():
    session.pop('admin', None)
    return redirect('/admin_login')


# ---------- TEAMS ----------
@app.route('/add_team', methods=['GET', 'POST'])
def add_team():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        cursor.execute(
            "INSERT INTO teams (name, captain, coach) VALUES (%s, %s, %s)",
            (request.form['name'], request.form['captain'], request.form['coach'])
        )
        conn.commit()
        flash("Team added")

    cursor.close()
    conn.close()
    return render_template('add_team.html')


@app.route('/teams')
def view_teams():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM teams")
    teams = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('teams.html', teams=teams)


# ---------- STADIUM ----------
@app.route('/add_stadium', methods=['GET', 'POST'])
def add_stadium():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        cursor.execute(
            "INSERT INTO stadium (name, location, capacity) VALUES (%s, %s, %s)",
            (request.form['name'], request.form['location'], request.form['capacity'])
        )
        conn.commit()
        flash("Stadium added")

    cursor.close()
    conn.close()
    return render_template('add_stadium.html')


@app.route('/view_stadiums')
def view_stadiums():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM stadium")
    stadiums = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('view_stadiums.html', stadiums=stadiums)


# ---------- MATCH ----------
@app.route('/add_match', methods=['GET', 'POST'])
def add_match():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT teamid, name FROM teams")
    teams = cursor.fetchall()

    cursor.execute("SELECT stadiumid, name FROM stadium")
    stadiums = cursor.fetchall()

    if request.method == 'POST':
        cursor.execute(
            "INSERT INTO matches (team1_id, team2_id, match_date, stadiumid) VALUES (%s, %s, %s, %s)",
            (request.form['team1'], request.form['team2'], request.form['match_date'], request.form['stadium'])
        )
        conn.commit()
        flash("Match added")

    cursor.close()
    conn.close()
    return render_template('add_match.html', teams=teams, stadiums=stadiums)


# ---------- APP RUN (RAILWAY FIX) ----------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)