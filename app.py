from flask import Flask, render_template, request, redirect, session
from gemini_service import (
    generate_quiz,
    generate_feedback,
    generate_learning_roadmap,
    generate_viva_question,
    evaluate_viva_answer
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
    get_topic_analysis
)

app = Flask(__name__)

app.secret_key = "ai_quiz_builder_secret"

generated_questions = []
current_topic = ""
current_difficulty = ""

init_db()


@app.route("/")
def home():

    if "username" not in session:
        return redirect("/login")

    stats = get_dashboard_stats()

    history_data = get_history()

    chart_labels = []
    chart_scores = []

    for row in reversed(history_data[:10]):

        chart_labels.append(f"Quiz {row[0]}")
        chart_scores.append(row[4])

    return render_template(
        "index.html",
        stats=stats,
        history=history_data[:5],
        username=session["username"],
        chart_labels=chart_labels,
        chart_scores=chart_scores
    )



# REGISTER

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        success = register_user(
            username,
            password
        )

        if success:
            return redirect("/login")

        return "Username already exists"

    return render_template("register.html")


# LOGIN

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = login_user(
            username,
            password
        )

        if user:

            session["username"] = username

            return redirect("/")

        return "Invalid Username or Password"

    return render_template("login.html")


# LOGOUT

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# QUIZ

@app.route("/quiz", methods=["POST"])
def quiz():

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

        achievement = None

    if percentage == 100:
        achievement = "🏆 Perfect Score"

    elif percentage >= 80:
        achievement = "🔥 Quiz Master"

    elif percentage >= 60:
        achievement = "🚀 Fast Learner"

    else:
        achievement = "📚 Keep Learning"

    save_result(
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

    history_data = get_history()

    return render_template(
        "history.html",
        history=history_data
    )


# DASHBOARD

@app.route("/dashboard")
def dashboard():

    stats = get_dashboard_stats()

    topic_data = get_topic_analysis()

    strong_topics = []
    weak_topics = []

    for topic, avg_score in topic_data:

        if avg_score >= 70:
            strong_topics.append(topic)
        else:
            weak_topics.append(topic)

    roadmap = ""

    if weak_topics:
        roadmap = f"""
Focus on improving:
{', '.join(weak_topics)}

Study Plan:
• Revise fundamentals
• Practice quizzes daily
• Review incorrect answers
• Retake quizzes weekly

Goal:
Reach 70%+ average score in all weak topics.
"""

    return render_template(
        "dashboard.html",
        stats=stats,
        strong_topics=strong_topics,
        weak_topics=weak_topics,
        roadmap=roadmap
    )

@app.route("/leaderboard")
def leaderboard():

    data = get_leaderboard()

    return render_template(
        "leaderboard.html",
        leaderboard=data
    )

@app.route("/viva")
def viva():

    return render_template(
        "viva.html"
    )

@app.route("/start_viva", methods=["POST"])
def start_viva():

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

    topic = request.form["topic"]
    question = request.form["question"]
    answer = request.form["answer"]

    feedback = evaluate_viva_answer(
        topic,
        question,
        answer
    )

    score = 0

    save_viva_result(
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