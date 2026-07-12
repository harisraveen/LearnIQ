import sqlite3


def init_db():

    conn = sqlite3.connect("quiz_history.db")

    cursor = conn.cursor()

    # Users Table with email and joined_date
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        email TEXT UNIQUE,
        joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Quiz History Table with username
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT,
        score INTEGER,
        total INTEGER,
        percentage INTEGER,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        username TEXT
    )
    """)

    # Viva History Table with username
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS viva_history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT,
        question TEXT,
        answer TEXT,
        score INTEGER,
        feedback TEXT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        username TEXT
    )
    """)

    # Schema Migrations (in case DB already exists and needs new columns)
    cursor.execute("PRAGMA table_info(users)")
    user_cols = [row[1] for row in cursor.fetchall()]
    if "email" not in user_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
    if "joined_date" not in user_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN joined_date TIMESTAMP")

    cursor.execute("PRAGMA table_info(history)")
    hist_cols = [row[1] for row in cursor.fetchall()]
    if "username" not in hist_cols:
        cursor.execute("ALTER TABLE history ADD COLUMN username TEXT")

    cursor.execute("PRAGMA table_info(viva_history)")
    viva_cols = [row[1] for row in cursor.fetchall()]
    if "username" not in viva_cols:
        cursor.execute("ALTER TABLE viva_history ADD COLUMN username TEXT")

    conn.commit()
    conn.close()


# USER FUNCTIONS

def register_user(username, password, email):

    conn = sqlite3.connect("quiz_history.db")
    cursor = conn.cursor()

    try:

        cursor.execute("""
        INSERT INTO users(username, password, email)
        VALUES (?, ?, ?)
        """, (username, password, email))

        conn.commit()

        return True

    except Exception as e:
        print("Registration error:", e)
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


def check_username_exists(username):
    conn = sqlite3.connect("quiz_history.db")
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE username=?", (username,))
    res = cursor.fetchone()
    conn.close()
    return res is not None


def check_email_exists(email):
    conn = sqlite3.connect("quiz_history.db")
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE email=?", (email,))
    res = cursor.fetchone()
    conn.close()
    return res is not None


def update_user_profile(old_username, new_username, new_email):
    conn = sqlite3.connect("quiz_history.db")
    cursor = conn.cursor()
    try:
        cursor.execute("""
        UPDATE users
        SET username=?, email=?
        WHERE username=?
        """, (new_username, new_email, old_username))
        
        # Also update history and viva history to keep user's records linked
        cursor.execute("UPDATE history SET username=? WHERE username=?", (new_username, old_username))
        cursor.execute("UPDATE viva_history SET username=? WHERE username=?", (new_username, old_username))
        
        conn.commit()
        return True
    except Exception as e:
        print("Update profile error:", e)
        return False
    finally:
        conn.close()


def update_user_password(username, new_password):
    conn = sqlite3.connect("quiz_history.db")
    cursor = conn.cursor()
    try:
        cursor.execute("""
        UPDATE users
        SET password=?
        WHERE username=?
        """, (new_password, username))
        conn.commit()
        return True
    except Exception as e:
        print("Update password error:", e)
        return False
    finally:
        conn.close()


def get_user_stats(username):
    conn = sqlite3.connect("quiz_history.db")
    cursor = conn.cursor()
    
    # User details
    cursor.execute("SELECT email, joined_date FROM users WHERE username=?", (username,))
    user_info = cursor.fetchone()
    email = user_info[0] if user_info else ""
    joined_date = user_info[1] if user_info else ""

    # Quiz stats
    cursor.execute("SELECT COUNT(*), AVG(percentage), MAX(percentage) FROM history WHERE username=?", (username,))
    quiz_stats = cursor.fetchone()
    total_quizzes = quiz_stats[0] or 0
    avg_score = round(quiz_stats[1] or 0)
    highest_score = quiz_stats[2] or 0

    # Viva stats
    cursor.execute("SELECT COUNT(*) FROM viva_history WHERE username=?", (username,))
    total_vivas = cursor.fetchone()[0] or 0

    conn.close()
    return {
        "username": username,
        "email": email,
        "joined_date": joined_date,
        "total_quizzes": total_quizzes,
        "total_vivas": total_vivas,
        "highest_score": highest_score,
        "average_score": avg_score
    }


def get_learning_streak(username):
    conn = sqlite3.connect("quiz_history.db")
    cursor = conn.cursor()
    
    # Fetch all dates from history & viva_history for this user
    cursor.execute("""
    SELECT DISTINCT date(date) as act_date FROM history WHERE username=?
    UNION
    SELECT DISTINCT date(date) as act_date FROM viva_history WHERE username=?
    ORDER BY act_date DESC
    """, (username, username))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return 0

    from datetime import datetime, timedelta
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    dates = [datetime.strptime(r[0], "%Y-%m-%d").date() for r in rows]

    # Check if they have active today or yesterday to continue the streak
    if dates[0] != today and dates[0] != yesterday:
        return 0

    streak = 1
    for i in range(len(dates) - 1):
        diff = (dates[i] - dates[i+1]).days
        if diff == 1:
            streak += 1
        elif diff > 1:
            break
    return streak


def get_recent_activity(username, limit=5):
    conn = sqlite3.connect("quiz_history.db")
    cursor = conn.cursor()
    cursor.execute("""
    SELECT 'Quiz' as type, topic, percentage as score, date FROM history WHERE username=?
    UNION ALL
    SELECT 'Viva' as type, topic, score * 10 as score, date FROM viva_history WHERE username=?
    ORDER BY date DESC
    LIMIT ?
    """, (username, username, limit))
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_latest_quiz(username):
    conn = sqlite3.connect("quiz_history.db")
    cursor = conn.cursor()
    cursor.execute("""
    SELECT topic, score, total, percentage, date FROM history WHERE username=? ORDER BY id DESC LIMIT 1
    """, (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "topic": row[0],
            "score": row[1],
            "total": row[2],
            "percentage": row[3],
            "date": row[4]
        }
    return None


# QUIZ FUNCTIONS

def save_result(username, topic, score, total, percentage):

    conn = sqlite3.connect("quiz_history.db")

    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO history(
        username,
        topic,
        score,
        total,
        percentage
    )
    VALUES (?, ?, ?, ?, ?)
    """, (
        username,
        topic,
        score,
        total,
        percentage
    ))

    conn.commit()
    conn.close()


def save_viva_result(
    username,
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
        username,
        topic,
        question,
        answer,
        score,
        feedback
    )
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        username,
        topic,
        question,
        answer,
        score,
        feedback
    ))

    conn.commit()
    conn.close()


def get_history(username=None):

    conn = sqlite3.connect("quiz_history.db")

    cursor = conn.cursor()

    if username:
        cursor.execute("""
        SELECT *
        FROM history
        WHERE username=?
        ORDER BY id DESC
        """, (username,))
    else:
        cursor.execute("""
        SELECT *
        FROM history
        ORDER BY id DESC
        """)

    rows = cursor.fetchall()

    conn.close()

    return rows


def get_dashboard_stats(username=None):

    conn = sqlite3.connect("quiz_history.db")

    cursor = conn.cursor()

    if username:
        cursor.execute("SELECT COUNT(*) FROM history WHERE username=?", (username,))
        total_quizzes = cursor.fetchone()[0]

        cursor.execute("SELECT AVG(percentage) FROM history WHERE username=?", (username,))
        average_score = cursor.fetchone()[0]

        cursor.execute("SELECT MAX(percentage) FROM history WHERE username=?", (username,))
        highest_score = cursor.fetchone()[0]

        cursor.execute("SELECT MIN(percentage) FROM history WHERE username=?", (username,))
        lowest_score = cursor.fetchone()[0]

        cursor.execute("""
        SELECT topic
        FROM history
        WHERE username=?
        ORDER BY id DESC
        LIMIT 1
        """, (username,))
        latest_topic = cursor.fetchone()
    else:
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
        IFNULL(username, 'Anonymous') as user_name,
        MAX(percentage) as best_score,
        MAX(date),
        topic
    FROM history
    GROUP BY user_name, topic
    ORDER BY best_score DESC
    LIMIT 10
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows


def get_topic_analysis(username=None):

    conn = sqlite3.connect("quiz_history.db")
    cursor = conn.cursor()

    if username:
        cursor.execute("""
            SELECT topic,
                   AVG(percentage)
            FROM history
            WHERE username=?
            GROUP BY topic
        """, (username,))
    else:
        cursor.execute("""
            SELECT topic,
                   AVG(percentage)
            FROM history
            GROUP BY topic
        """)

    data = cursor.fetchall()

    conn.close()

    return data
