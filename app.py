from flask import Flask, render_template, request, redirect, session
import re
from gemini_service import (
    generate_quiz,
    generate_feedback,
    generate_learning_roadmap,
    generate_viva_question,
    evaluate_viva_answer,
    generate_learning_insights
)
from database import (
    init_db,
    save_result,
    save_viva_result,
    get_history,
    get_dashboard_stats,
    register_user,
    login_user,
    get_leaderboard,
    get_topic_analysis,
    check_username_exists,
    check_email_exists,
    update_user_profile,
    update_user_password,
    get_user_stats,
    get_learning_streak,
    get_recent_activity,
    get_latest_quiz
)

app = Flask(__name__)

import os

app.secret_key = os.getenv("SECRET_KEY", "ai_quiz_builder_secret")

generated_questions = []
current_topic = ""
current_difficulty = ""

init_db()


@app.route("/")
def home():

    if "username" not in session:
        return redirect("/login")

    username = session["username"]
    stats = get_dashboard_stats(username)
    history_data = get_history(username)

    chart_labels = []
    chart_scores = []

    for row in reversed(history_data[:10]):
        chart_labels.append(f"Quiz {row[0]}")
        chart_scores.append(row[4])

    return render_template(
        "index.html",
        stats=stats,
        history=history_data[:5],
        username=username,
        chart_labels=chart_labels,
        chart_scores=chart_scores
    )



# REGISTER

@app.route("/register", methods=["GET", "POST"])
def register():
    if "username" in session:
        return redirect("/")

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Server-side validation
        # 1. Mandatory fields
        if not username or not email or not password or not confirm_password:
            return render_template("register.html", error="All fields are required.", username=username, email=email)

        # 2. Username format check (3-20 chars, alphanumeric/underscore)
        if not re.match("^[a-zA-Z0-9_]{3,20}$", username):
            return render_template("register.html", error="Username must be 3-20 characters and contain only letters, numbers, or underscores.", username=username, email=email)

        # 3. Email format check
        if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
            return render_template("register.html", error="Please enter a valid email address.", username=username, email=email)

        # 4. Password validation (Min 8, Upper, Lower, Num, Special)
        password_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
        if not re.match(password_pattern, password):
            return render_template("register.html", error="Password does not meet validation requirements (min 8 characters, mixed case, a number, and a special character).", username=username, email=email)

        # 5. Confirm password match
        if password != confirm_password:
            return render_template("register.html", error="Passwords do not match.", username=username, email=email)

        # 6. Check duplicates
        if check_username_exists(username):
            return render_template("register.html", error="Username already exists.", username=username, email=email)

        if check_email_exists(email):
            return render_template("register.html", error="Email is already registered.", username=username, email=email)

        # Proceed to register
        success = register_user(username, password, email)
        if success:
            return redirect("/login")

        return render_template("register.html", error="Registration failed. Please try again.", username=username, email=email)

    return render_template("register.html")


# LOGIN

@app.route("/login", methods=["GET", "POST"])
def login():
    if "username" in session:
        return redirect("/")

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = login_user(username, password)

        if user:
            session["username"] = username
            return redirect("/")

        return render_template("login.html", error="Invalid username or password.", username=username)

    return render_template("login.html")


# LOGOUT

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# QUIZ

@app.route("/quiz", methods=["POST"])
def quiz():
    if "username" not in session:
        return redirect("/login")

    global generated_questions
    global current_topic
    global current_difficulty

    current_topic = request.form["topic"]
    current_difficulty = request.form["difficulty"]
    count = int(request.form["count"])

    generated_questions = generate_quiz(
        current_topic,
        current_difficulty,
        count
    )

    return render_template(
        "quiz.html",
        topic=current_topic,
        questions=generated_questions
    )


# RESULT

@app.route("/result", methods=["POST"])
def result():
    if "username" not in session:
        return redirect("/login")

    username = session["username"]
    results = []
    score = 0

    for i, q in enumerate(generated_questions):
        user_answer = request.form.get(f"q{i}")
        is_correct = user_answer == q["answer"]

        if is_correct:
            score += 1

        results.append({
            "question": q["question"],
            "user_answer": user_answer,
            "correct_answer": q["answer"],
            "is_correct": is_correct
        })

    total = len(generated_questions)

    if total == 0:
        return redirect("/")

    wrong = total - score
    percentage = round((score / total) * 100)
    xp = percentage * 10

    level = 1
    if xp >= 5000:
        level = 5
    elif xp >= 3000:
        level = 4
    elif xp >= 2000:
        level = 3
    elif xp >= 1000:
        level = 2

    if percentage == 100:
        achievement = "🏆 Perfect Score"
    elif percentage >= 80:
        achievement = "🔥 Quiz Master"
    elif percentage >= 60:
        achievement = "🚀 Fast Learner"
    else:
        achievement = "📚 Keep Learning"

    save_result(
        username,
        current_topic,
        score,
        total,
        percentage
    )

    if percentage >= 80:
        message = "🏆 Excellent!"
    elif percentage >= 50:
        message = "👍 Good Job!"
    else:
        message = "📚 Keep Practicing!"

    feedback = generate_feedback(
        current_topic,
        percentage
    )

    return render_template(
        "result.html",
        score=score,
        total=total,
        wrong=wrong,
        percentage=percentage,
        message=message,
        results=results,
        feedback=feedback,
        xp=xp,
        level=level,
        achievement=achievement
    )


# HISTORY

@app.route("/history")
def history():
    if "username" not in session:
        return redirect("/login")

    username = session["username"]
    history_data = get_history(username)

    return render_template(
        "history.html",
        history=history_data
    )


# DASHBOARD

@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect("/login")

    username = session["username"]
    stats = get_dashboard_stats(username)
    topic_data = get_topic_analysis(username)
    streak = get_learning_streak(username)
    recent_activity = get_recent_activity(username, limit=5)
    latest_quiz = get_latest_quiz(username)

    strong_topics = []
    weak_topics = []

    for topic, avg_score in topic_data:
        if avg_score >= 70:
            strong_topics.append(topic)
        else:
            weak_topics.append(topic)

    roadmap = ""
    if weak_topics:
        roadmap = generate_learning_roadmap(weak_topics)
    else:
        roadmap = "Congratulations! You have achieved 70%+ average scores in all attempted topics. Keep exploring new subjects!"

    # Chart datasets
    history_data = get_history(username)
    weekly_labels = []
    weekly_scores = []
    
    # Grab last 7 quiz attempts
    for row in reversed(history_data[:7]):
        # row[1] is topic, row[5] is timestamp (using f"{topic} ({date})")
        date_str = row[5][:10] if row[5] else ""
        weekly_labels.append(f"{row[1]} ({date_str})")
        weekly_scores.append(row[4])

    topic_labels = [row[0] for row in topic_data]
    topic_scores = [round(row[1]) for row in topic_data]

    # Generate insights from AI
    insights = generate_learning_insights(stats, topic_data)

    return render_template(
        "dashboard.html",
        stats=stats,
        streak=streak,
        recent_activity=recent_activity,
        latest_quiz=latest_quiz,
        weekly_labels=weekly_labels,
        weekly_scores=weekly_scores,
        topic_labels=topic_labels,
        topic_scores=topic_scores,
        strong_topics=strong_topics,
        weak_topics=weak_topics,
        roadmap=roadmap,
        insights=insights
    )


# PROFILE

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "username" not in session:
        return redirect("/login")

    username = session["username"]
    error = None
    success = None

    if request.method == "POST":
        action = request.form.get("action")

        if action == "update_profile":
            new_username = request.form.get("username", "").strip()
            new_email = request.form.get("email", "").strip()

            if not new_username or not new_email:
                error = "Username and Email are required."
            elif not re.match("^[a-zA-Z0-9_]{3,20}$", new_username):
                error = "Username must be 3-20 characters and contain only letters, numbers, or underscores."
            elif not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", new_email):
                error = "Please enter a valid email address."
            else:
                # Check uniqueness if username changed
                if new_username != username and check_username_exists(new_username):
                    error = "Username already exists."
                else:
                    # Check uniqueness if email changed
                    current_stats = get_user_stats(username)
                    if new_email != current_stats["email"] and check_email_exists(new_email):
                        error = "Email is already registered."
                    else:
                        res = update_user_profile(username, new_username, new_email)
                        if res:
                            session["username"] = new_username
                            username = new_username
                            success = "Profile details updated successfully."
                        else:
                            error = "Failed to update profile details."

        elif action == "change_password":
            current_password = request.form.get("current_password", "")
            new_password = request.form.get("new_password", "")
            confirm_new_password = request.form.get("confirm_new_password", "")

            user = login_user(username, current_password)
            if not user:
                error = "Current password is incorrect."
            elif not new_password:
                error = "New password cannot be empty."
            elif password_pattern := r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$":
                if not re.match(password_pattern, new_password):
                    error = "New password does not meet criteria."
            elif new_password != confirm_new_password:
                error = "New passwords do not match."
            else:
                res = update_user_password(username, new_password)
                if res:
                    success = "Password updated successfully."
                else:
                    error = "Failed to update password."

    stats = get_user_stats(username)
    return render_template(
        "profile.html",
        stats=stats,
        error=error,
        success=success
    )


# LEADERBOARD

@app.route("/leaderboard")
def leaderboard():
    if "username" not in session:
        return redirect("/login")

    data = get_leaderboard()

    return render_template(
        "leaderboard.html",
        leaderboard=data
    )


# VIVA

@app.route("/viva")
def viva():
    if "username" not in session:
        return redirect("/login")

    return render_template(
        "viva.html"
    )


@app.route("/start_viva", methods=["POST"])
def start_viva():
    if "username" not in session:
        return redirect("/login")

    topic = request.form["topic"]
    difficulty = request.form["difficulty"]

    question = generate_viva_question(
        topic,
        difficulty
    )

    return render_template(
        "viva_question.html",
        topic=topic,
        question=question
    )


@app.route("/evaluate_viva", methods=["POST"])
def evaluate_viva():
    if "username" not in session:
        return redirect("/login")

    username = session["username"]
    topic = request.form["topic"]
    question = request.form["question"]
    answer = request.form["answer"]

    feedback = evaluate_viva_answer(
        topic,
        question,
        answer
    )

    # Extract score out of feedback if possible, else 0
    score = 0
    try:
        # Find something like "Score: 8/10" or "8/10"
        match = re.search(r"(\d+)/10", feedback)
        if match:
            score = int(match.group(1))
    except Exception as e:
        print("Score extraction warning:", e)

    save_viva_result(
        username,
        topic,
        question,
        answer,
        score,
        feedback
    )

    return render_template(
        "viva_result.html",
        topic=topic,
        question=question,
        answer=answer,
        feedback=feedback
    )


if __name__ == "__main__":
    app.run(debug=True)