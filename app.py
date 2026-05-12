from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import sqlite3
import os
import re
import bcrypt
from datetime import datetime
from scam_detector import analyze_job_description

app = Flask(__name__)
app.secret_key = 'your_secret_key_change_this_in_production'

# On Vercel, we must use /tmp for any file writes.
# Note: /tmp is ephemeral and will be cleared when the function restarts.
if os.environ.get('VERCEL'):
    DATABASE = '/tmp/job_detector.db'
    # Copy initial DB to /tmp if it exists in the repo but not in /tmp
    if not os.path.exists(DATABASE) and os.path.exists('job_detector.db'):
        import shutil
        shutil.copy('job_detector.db', DATABASE)
else:
    DATABASE = 'job_detector.db'

def get_db_connection():
    # Use check_same_thread=False for sqlite in multi-threaded environments like Flask
    conn = sqlite3.connect(DATABASE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists(DATABASE):
        conn = get_db_connection()
        with open('schema.sql', 'r') as f:
            conn.executescript(f.read())
        conn.commit()
        conn.close()
        print("Database initialized.")

# Initialize the database on startup
init_db()

# ==================================================================
# AUTH ROUTES
# ==================================================================

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name     = request.form['name'].strip()
        email    = request.form['email'].strip().lower()
        password = request.form['password']

        if not name or not email or not password:
            flash('All fields are required.', 'error')
            return redirect(url_for('register'))

        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address.', 'error')
            return redirect(url_for('register'))

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        existing = cursor.fetchone()

        if existing:
            conn.close()
            flash('Email already registered. Please log in.', 'error')
            return redirect(url_for('register'))

        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute(
            'INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
            (name, email, hashed_pw)
        )
        conn.commit()
        conn.close()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form['email'].strip().lower()
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()

        if user:
            # Check password
            db_password = user['password']
            is_valid = False
            
            # If stored password starts with $2b$ or $2a$, it's hashed
            if db_password.startswith('$2b$') or db_password.startswith('$2a$'):
                try:
                    is_valid = bcrypt.checkpw(password.encode('utf-8'), db_password.encode('utf-8'))
                except ValueError:
                    pass
            else:
                # Plain text password fallback
                if password == db_password:
                    is_valid = True
                    # Upgrade to bcrypt on the fly
                    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    conn = get_db_connection()
                    conn.execute('UPDATE users SET password = ? WHERE id = ?', (hashed_pw, user['id']))
                    conn.commit()
                    conn.close()

            if is_valid:
                session['user_id']   = user['id']
                session['user_name'] = user['name']
                return redirect(url_for('dashboard'))

        flash('Invalid email or password.', 'error')
        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ==================================================================
# MAIN PAGES
# ==================================================================

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', user_name=session['user_name'])


@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    # SQLite uses comma for GROUP_CONCAT separator
    cursor.execute(
        '''SELECT j.id, j.job_text, j.scam_score, j.result, j.created_at,
                  GROUP_CONCAT(f.flag_reason, '||') AS flags
           FROM jobs j
           LEFT JOIN flags f ON f.job_id = j.id
           WHERE j.user_id = ?
           GROUP BY j.id
           ORDER BY j.created_at DESC
           LIMIT 50''',
        (session['user_id'],)
    )
    rows = cursor.fetchall()
    conn.close()

    jobs = []
    for row in rows:
        job = dict(row)
        # Parse the date string from SQLite into a datetime object
        if isinstance(job['created_at'], str):
            try:
                # Handle both formats with and without fractional seconds
                if '.' in job['created_at']:
                    job['created_at'] = datetime.strptime(job['created_at'], '%Y-%m-%d %H:%M:%S.%f')
                else:
                    job['created_at'] = datetime.strptime(job['created_at'], '%Y-%m-%d %H:%M:%S')
            except Exception:
                pass # Fallback if parsing fails

        job['flags'] = job['flags'].split('||') if job['flags'] else []
        job['job_preview'] = job['job_text'][:180] + ('…' if len(job['job_text']) > 180 else '')
        jobs.append(job)

    return render_template('history.html', jobs=jobs, user_name=session['user_name'])


# ==================================================================
# API ENDPOINT
# ==================================================================

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    job_text = (data or {}).get('job_text', '').strip()

    if not job_text:
        return jsonify({'error': 'Job description cannot be empty.'}), 400

    if len(job_text) < 20:
        return jsonify({'error': 'Please enter a more detailed job description.'}), 400

    # --- run scam analysis ---
    result = analyze_job_description(job_text)

    # --- persist to DB ---
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO jobs (user_id, job_text, scam_score, result, created_at) VALUES (?, ?, ?, ?, ?)',
        (session['user_id'], job_text, result['scam_score'], result['result'], datetime.now())
    )
    job_id = cursor.lastrowid

    for reason in result['reasons']:
        cursor.execute('INSERT INTO flags (job_id, flag_reason) VALUES (?, ?)', (job_id, reason))

    conn.commit()
    conn.close()

    return jsonify(result)


@app.route('/delete/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    conn = get_db_connection()
    cursor = conn.cursor()
    # Ensure the job belongs to this user
    cursor.execute('SELECT id FROM jobs WHERE id = ? AND user_id = ?', (job_id, session['user_id']))
    job = cursor.fetchone()
    if not job:
        conn.close()
        return jsonify({'error': 'Not found'}), 404

    cursor.execute('DELETE FROM flags WHERE job_id = ?', (job_id,))
    cursor.execute('DELETE FROM jobs WHERE id = ?', (job_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


# ==================================================================
if __name__ == '__main__':
    app.run(debug=True, port=5000)
