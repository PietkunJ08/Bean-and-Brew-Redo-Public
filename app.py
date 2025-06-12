from flask import Flask, render_template, request, redirect, url_for, flash, session
from db_create import create_users_db
import sqlite3, hashlib, os

app = Flask(__name__)
app.secret_key = '56'
db_locale = 'users.db'

if not os.path.exists(db_locale):
    create_users_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        connection = sqlite3.connect(db_locale)
        cursor = connection.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            connection.commit()
            flash('Signup successful! Please log in')
            return redirect(url_for('signup'))
        except sqlite3.IntegrityError:
            flash('Username already exists')
            return redirect(url_for('signup'))
        finally:
            connection.close()
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        connection = sqlite3.connect(db_locale)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        connection.close()
        if user:
            session['username'] = username
            flash("Login successful!")
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials.')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    else:
        flash('Please log in first.')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logged out.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)