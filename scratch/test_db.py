import sqlite3
import bcrypt

DATABASE = 'job_detector.db'

def test_registration():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Clean up previous tests
    cursor.execute('DELETE FROM users WHERE email = ?', ('test@example.com',))
    
    name = "Test User"
    email = "test@example.com"
    password = "password123"
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    try:
        cursor.execute(
            'INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
            (name, email, hashed_pw)
        )
        conn.commit()
        print("Registration successful!")
    except Exception as e:
        print(f"Registration failed: {e}")
    
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    if user:
        print(f"User found: {user[1]} ({user[2]})")
    else:
        print("User not found!")
    
    conn.close()

if __name__ == '__main__':
    test_registration()
