import sqlite3
import bcrypt

DATABASE_NAME = "cloudbooth.db"

def get_db_connection():
    """Creates and returns a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def create_user_table():
    """Creates the 'users' table if it doesn't already exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            level INTEGER NOT NULL DEFAULT 1,
            xp INTEGER NOT NULL DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def add_user(username, password):
    """Adds a new user to the database with a hashed password."""
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, hashed_password.decode('utf-8'))
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # This error occurs if the username is already taken
        return False
    finally:
        conn.close()

def check_user(username, password):
    """Verifies a user's credentials against the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    user_record = cursor.fetchone()
    conn.close()
    if user_record and bcrypt.checkpw(password.encode('utf-8'), user_record['password_hash'].encode('utf-8')):
        return True
    return False

def get_user_profile(username):
    """Retrieves a user's profile (level and XP)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT level, xp FROM users WHERE username = ?", (username,))
    profile = cursor.fetchone()
    conn.close()
    if profile:
        return dict(profile)
    return None

def update_user_profile(username, level, xp):
    """Updates a user's level and XP in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET level = ?, xp = ? WHERE username = ?",
        (level, xp, username)
    )
    conn.commit()
    conn.close()

def get_xp_for_next_level(level):
    """Calculates the XP needed for the next level."""
    return int(100 * (1.5 ** (level - 1)))

def add_xp(profile, amount):
    """Adds XP and handles leveling up."""
    profile['xp'] += amount
    xp_needed = get_xp_for_next_level(profile['level'])
    leveled_up = False
    while profile['xp'] >= xp_needed:
        profile['level'] += 1
        profile['xp'] -= xp_needed
        xp_needed = get_xp_for_next_level(profile['level'])
        leveled_up = True
    return leveled_up

# Initialize the database and table when this module is imported
create_user_table()
