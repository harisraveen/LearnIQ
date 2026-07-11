import sqlite3


def init_db():

    conn = sqlite3.connect("quiz_history.db")

    cursor = conn.cursor()

    # Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    # Quiz History Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT,
        score INTEGER,
        total INTEGER,
        percentage INTEGER,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
CREATE TABLE IF NOT EXISTS viva_history(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT,
    question TEXT,
    answer TEXT,
    score INTEGER,
    feedback TEXT,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

    conn.commit()
    conn.close()


# USER FUNCTIONS

def register_user(username, password):

    conn = sqlite3.connect("quiz_history.db")
    cursor = conn.cursor()

    try:

        cursor.execute("""
        INSERT INTO users(username, password)
        VALUES (?, ?)
        """, (username, password))

        conn.commit()

        return True

    except:

        return False

    finally:

        conn.close()


def login_user(username, password):

    conn = sqlite3.connect("quiz_history.db")

    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM users
    WHERE username=? AND password=?
    """, (username, password))

    user = cursor.fetchone()

    conn.close()

    return user


# QUIZ FUNCTIONS

def save_result(topic, score, total, percentage):

    conn = sqlite3.connect("quiz_history.db")

    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO history(
        topic,
        score,
        total,
        percentage
    )
    VALUES (?, ?, ?, ?)
    """, (
        topic,
        score,
        total,
        percentage
    ))

    conn.commit()
    conn.close()

def save_viva_result(
    topic,
    question,
    answer,
    score,
    feedback
):

    conn = sqlite3.connect("quiz_history.db")

    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO viva_history(
        topic,
        question,
        answer,
        score,
        feedback
    )
    VALUES (?, ?, ?, ?, ?)
    """, (
        topic,
        question,
        answer,
        score,
        feedback
    ))

    conn.commit()
    conn.close()


def get_history():

    conn = sqlite3.connect("quiz_history.db")

    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM history
    ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows


def get_dashboard_stats():

    conn = sqlite3.connect("quiz_history.db")

    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM history")
    total_quizzes = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(percentage) FROM history")
    average_score = cursor.fetchone()[0]

    cursor.execute("SELECT MAX(percentage) FROM history")
    highest_score = cursor.fetchone()[0]

    cursor.execute("SELECT MIN(percentage) FROM history")
    lowest_score = cursor.fetchone()[0]

    cursor.execute("""
    SELECT topic
    FROM history
    ORDER BY id DESC
    LIMIT 1
    """)

    latest_topic = cursor.fetchone()

    conn.close()

    return {
        "total_quizzes": total_quizzes,
        "average_score": round(average_score or 0),
        "highest_score": highest_score or 0,
        "lowest_score": lowest_score or 0,
        "latest_topic": latest_topic[0] if latest_topic else "None"
    }

def get_leaderboard():

    conn = sqlite3.connect("quiz_history.db")

    cursor = conn.cursor()

    cursor.execute("""
SELECT
    topic,
    MAX(percentage) as best_score,
    MAX(date)
FROM history
GROUP BY topic
ORDER BY best_score DESC
LIMIT 10
""")

    rows = cursor.fetchall()

    conn.close()

    return rows

def get_topic_analysis():

    conn = sqlite3.connect("quiz_history.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT topic,
               AVG(percentage)
        FROM history
        GROUP BY topic
    """)

    data = cursor.fetchall()

    conn.close()

    return data

