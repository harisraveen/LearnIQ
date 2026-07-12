import google.generativeai as genai
import json
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")


def generate_quiz(topic, difficulty="Medium", count=5):

    prompt = f"""
    Generate {count} multiple choice questions about {topic}.

    Difficulty Level: {difficulty}

    Rules:

    1. Each question must have exactly 4 options.
    2. Only one correct answer.
    3. Questions should match the difficulty level.
    4. Return ONLY valid JSON.
    5. Do not include explanations.

    Example:

    [
      {{
        "question": "What is Python?",
        "options": [
          "Programming Language",
          "Database",
          "Browser",
          "Operating System"
        ],
        "answer": "Programming Language"
      }}
    ]
    """

    response = model.generate_content(prompt)

    text = response.text.strip()

    if text.startswith("```json"):
        text = text.replace("```json", "")
        text = text.replace("```", "")

    return json.loads(text.strip())


def generate_feedback(topic, percentage):

    prompt = f"""
    You are an expert AI Learning Coach.

    Topic: {topic}
    Student Score: {percentage}%

    Analyze the student's performance.

    Return a JSON object with the following keys and structure:
    {{
        "strengths": "a summary of what they did well (keep under 50 words)",
        "weaknesses": "a summary of areas to improve (keep under 50 words)",
        "recommended_topics": ["topic 1", "topic 2", "topic 3"],
        "roadmap": "step-by-step roadmap to master this topic (keep under 60 words)",
        "study_suggestions": "actionable study suggestions (keep under 50 words)"
    }}

    Rules:
    - Keep overall feedback detailed and precise
    - Return ONLY valid JSON
    - Do not wrap in ```json block or include explanations outside the JSON object
    """

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        if text.startswith("```json"):
            text = text.replace("```json", "")
            if text.endswith("```"):
                text = text[:-3]
        elif text.startswith("```"):
            text = text.replace("```", "")
            if text.endswith("```"):
                text = text[:-3]
        
        return json.loads(text.strip())
    except Exception as e:
        print("AI Feedback Generation Error:", e)
        # Fallback dictionary matching expectations
        return {
            "strengths": f"Demonstrated basic understanding of {topic}.",
            "weaknesses": f"Needs further practice in core concepts of {topic}.",
            "recommended_topics": [topic],
            "roadmap": f"1. Review fundamental theory.\n2. Complete practice quizzes.\n3. Analyze wrong answers.",
            "study_suggestions": "Dedicate 20 minutes daily to testing and flashcards."
        }


def generate_learning_roadmap(weak_topics):

    prompt = f"""
    You are an expert learning mentor.

    Weak Topics:
    {', '.join(weak_topics)}

    Create a personalized learning roadmap.

    Include:

    1. Learning Goal
    2. Week-wise Study Plan
    3. Recommended Concepts
    4. Expected Outcome

    Keep under 200 words.
    Plain text only.
    """

    response = model.generate_content(prompt)

    return response.text


def generate_learning_insights(stats, topic_data):
    if not topic_data:
        return "Complete quizzes to generate AI learning insights!"

    topics_summary = ", ".join([f"{t}: {round(s)}%" for t, s in topic_data])
    
    prompt = f"""
    You are an expert AI Learning Coach.
    Here are the overall learning metrics for the student:
    - Total Quizzes Taken: {stats['total_quizzes']}
    - Average Score: {stats['average_score']}%
    - Highest Score: {stats['highest_score']}%
    - Lowest Score: {stats['lowest_score']}%
    - Topic-wise Performance: {topics_summary}

    Generate 3-4 bullet points of high-level AI learning insights, highlighting their performance trends, core strengths, and specific areas where study habits could be improved.
    Keep it concise, professional, encouraging, and under 150 words. Plain text with dash (-) bullet points only.
    """

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("AI Insights Error:", e)
        return "- Practice more quizzes across topics to generate detailed learning insights!\n- Stay consistent with your study schedule to maintain your learning streak."


def generate_viva_question(topic, difficulty):

    prompt = f"""
    You are an expert university examiner.

    Topic: {topic}
    Difficulty: {difficulty}

    Generate ONE viva voce question.

    Rules:
    - Question only
    - No explanation
    - No answer
    - Interview style
    """

    response = model.generate_content(prompt)

    return response.text.strip()


def evaluate_viva_answer(topic, question, answer):

    prompt = f"""
You are an expert interviewer.

Topic: {topic}

Question:
{question}

Student Answer:
{answer}

Evaluate the answer.

Return:

Score: X/10

Feedback:
Short explanation.
"""

    response = model.generate_content(prompt)

    return response.text.strip()