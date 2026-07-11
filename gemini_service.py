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

    return json.loads(text)


def generate_feedback(topic, percentage):

    prompt = f"""
    You are an expert AI Learning Coach.

    Topic: {topic}
    Student Score: {percentage}%

    Analyze the student's performance.

    Return:

    1. Performance Summary
    2. Strong Areas
    3. Weak Areas
    4. Recommended Topics To Study Next
    5. Personalized Learning Roadmap

    Rules:
    - Keep under 200 words
    - Use bullet points
    - No markdown symbols
    - Plain text only
    """

    response = model.generate_content(prompt)

    return response.text

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