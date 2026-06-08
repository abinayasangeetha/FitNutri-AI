import sqlite3
import hashlib

DATABASE_NAME = "fitnutri.db"


def create_tables():

    conn = sqlite3.connect(DATABASE_NAME)

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS profiles (
        user_id TEXT PRIMARY KEY,
        age INTEGER,
        gender TEXT,
        height_cm REAL,
        weight_kg REAL,
        activity_level TEXT,
        goal TEXT,
        diet_preference TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       name TEXT,
       email TEXT UNIQUE,
       password TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversations (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       user_email TEXT,
       title TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER,
    role TEXT,
    message TEXT
    )
    """)

    conn.commit()
    conn.close()
def save_message(conversation_id, role, message):

    conn = sqlite3.connect(DATABASE_NAME)

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO chat_history
        (conversation_id, role, message)
        VALUES (?, ?, ?)
        """,
        (conversation_id, role, message)
    )

    conn.commit()
    conn.close()
def get_messages(conversation_id):

    conn = sqlite3.connect(DATABASE_NAME)

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT role, message
        FROM chat_history
        WHERE conversation_id=?
        ORDER BY id
        """,
        (conversation_id,)
    )

    rows = cursor.fetchall()

    conn.close()

    history = []

    for row in rows:

        history.append(
            {
                "role": row[0],
                "content": row[1]
            }
        )

    return history

def save_profile_db(user_id, profile):

    conn = sqlite3.connect(DATABASE_NAME)

    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR REPLACE INTO profiles
    (
        user_id,
        age,
        gender,
        height_cm,
        weight_kg,
        activity_level,
        goal,
        diet_preference
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
    (
        user_id,
        profile["age"],
        profile["gender"],
        profile["height_cm"],
        profile["weight_kg"],
        profile["activity_level"],
        profile["goal"],
        profile["diet_preference"]
    ))

    conn.commit()
    conn.close()

def get_profile_db(user_id):

    conn = sqlite3.connect(DATABASE_NAME)

    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        age,
        gender,
        height_cm,
        weight_kg,
        activity_level,
        goal,
        diet_preference
    FROM profiles
    WHERE user_id=?
    """, (user_id,))

    row = cursor.fetchone()

    conn.close()

    if not row:
        return None

    return {
        "age": row[0],
        "gender": row[1],
        "height_cm": row[2],
        "weight_kg": row[3],
        "activity_level": row[4],
        "goal": row[5],
        "diet_preference": row[6]
    }
def create_user(name, email, password):

    conn = sqlite3.connect(DATABASE_NAME)

    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO users
    (name, email, password)
    VALUES (?, ?, ?)
    """,
    (name, email, password))

    conn.commit()
    conn.close()
def get_user(email):

    conn = sqlite3.connect(DATABASE_NAME)

    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM users
    WHERE email = ?
    """,
    (email,))

    user = cursor.fetchone()

    conn.close()

    return user
def hash_password(password):

    return hashlib.sha256(
        password.encode()
    ).hexdigest()
def verify_password(
    password,
    hashed_password
):

    return (
        hash_password(password)
        == hashed_password
    )

def create_conversation(
    user_email,
    title
):

    conn = sqlite3.connect(DATABASE_NAME)

    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO conversations
    (user_email,title)
    VALUES (?,?)
    """,
    (user_email,title))

    conn.commit()

    conversation_id = cursor.lastrowid

    conn.close()

    return conversation_id

def get_conversations(
    user_email
):

    conn = sqlite3.connect(DATABASE_NAME)

    cursor = conn.cursor()

    cursor.execute("""
    SELECT id,title
    FROM conversations
    WHERE user_email=?
    ORDER BY id DESC
    """,
    (user_email,))

    rows = cursor.fetchall()

    conn.close()

    return rows

def update_conversation_title(
    conversation_id,
    title
):

    conn = sqlite3.connect(DATABASE_NAME)

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE conversations
        SET title=?
        WHERE id=?
        """,
        (title, conversation_id)
    )

    conn.commit()
    conn.close()