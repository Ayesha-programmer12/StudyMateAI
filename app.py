from flask import Flask, render_template, request
from dotenv import load_dotenv
from google import genai
import os
import time

load_dotenv()

app = Flask(__name__)

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

MODEL = "gemini-3.1-flash-lite"


def generate_ai(prompt):
    """Generate an AI response with automatic retries for temporary errors."""

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt
            )

            return response.text

        except Exception as e:
            error_text = str(e)

            if "503" in error_text or "UNAVAILABLE" in error_text:
                if attempt < 2:
                    time.sleep(3)
                    continue

                return "Gemini AI is temporarily busy. Please try again in a few seconds."

            return "Unable to connect to Gemini AI. Please try again."

    return "Unable to generate a response."


# ==================================================
# TOPIC EXPLAINER
# ==================================================

@app.route("/", methods=["GET", "POST"])
def home():

    answer = ""
    error = ""
    topic = ""
    level = "Beginner"

    if request.method == "POST":

        topic = request.form.get("topic", "").strip()
        level = request.form.get("level", "Beginner")

        if topic:

            if level == "Beginner":
                level_instruction = """
Explain the topic using very simple language.
Assume the student is learning the topic for the first time.
Avoid unnecessary technical terms.
"""

            elif level == "Intermediate":
                level_instruction = """
Explain the topic at an intermediate university-student level.
Include important technical concepts and examples.
"""

            else:
                level_instruction = """
Explain the topic at an advanced university level.
Include deeper technical concepts, practical applications,
and important details.
"""

            prompt = f"""
You are a helpful AI university tutor.

Topic:
{topic}

Student Level:
{level}

{level_instruction}

Use exactly this structure:

1. Simple Definition
2. Explanation
3. Real-life or Practical Example
4. Key Points

Make the explanation clear, educational, and easy to understand.
"""

            result = generate_ai(prompt)

            if result.startswith("Gemini AI") or result.startswith("Unable"):
                error = result
            else:
                answer = result

    return render_template(
        "index.html",
        answer=answer,
        error=error,
        topic=topic,
        level=level
    )


# ==================================================
# NOTES SUMMARIZER
# ==================================================

@app.route("/summarizer", methods=["GET", "POST"])
def summarizer():

    summary = ""
    error = ""
    notes = ""
    style = "Short Summary"

    if request.method == "POST":

        notes = request.form.get("notes", "").strip()
        style = request.form.get("style", "Short Summary")

        if notes:

            if style == "Short Summary":

                instruction = """
Create a short and easy-to-understand summary.
Keep only the most important information.
"""

            elif style == "Detailed Summary":

                instruction = """
Create a detailed summary.
Include the important concepts and explanations.
Use clear university-level language.
"""

            else:

                instruction = """
Convert the notes into clear and organized key points.
Use simple bullet points.
"""

            prompt = f"""
You are an AI study assistant.

{instruction}

Notes:

{notes}
"""

            result = generate_ai(prompt)

            if result.startswith("Gemini AI") or result.startswith("Unable"):
                error = result
            else:
                summary = result

    return render_template(
        "summarizer.html",
        summary=summary,
        error=error,
        notes=notes,
        style=style
    )


# ==================================================
# MCQ GENERATOR
# ==================================================

@app.route("/mcq", methods=["GET", "POST"])
def mcq():

    questions = ""
    error = ""
    notes = ""
    number = "5"

    if request.method == "POST":

        notes = request.form.get("notes", "").strip()
        number = request.form.get("number", "5")

        if notes:

            prompt = f"""
You are an AI university exam question generator.

Create exactly {number} multiple-choice questions based ONLY
on the provided notes.

Rules:

- Create exactly {number} questions.
- Each question must have four options.
- Options must be A, B, C, and D.
- Only one option must be correct.
- Questions should be clear and educational.
- Do not use information outside the notes.
- Show the correct answer after each question.
- Avoid duplicate questions.

Notes:

{notes}
"""

            result = generate_ai(prompt)

            if result.startswith("Gemini AI") or result.startswith("Unable"):
                error = result
            else:
                questions = result

    return render_template(
        "mcq.html",
        questions=questions,
        error=error,
        notes=notes,
        number=number
    )


# ==================================================
# PROMPT LAB
# ==================================================

@app.route("/prompt-lab", methods=["GET", "POST"])
def prompt_lab():

    result = ""
    error = ""
    technique = "Zero-Shot Prompting"
    task = ""

    if request.method == "POST":

        technique = request.form.get(
            "technique",
            "Zero-Shot Prompting"
        )

        task = request.form.get("task", "").strip()

        if task:

            # -----------------------------
            # ZERO-SHOT PROMPTING
            # -----------------------------

            if technique == "Zero-Shot Prompting":

                prompt = f"""
You are demonstrating Zero-Shot Prompting.

Answer the user's task directly.
Do not use examples to guide the answer.

Task:

{task}
"""


            # -----------------------------
            # FEW-SHOT PROMPTING
            # -----------------------------

            elif technique == "Few-Shot Prompting":

                prompt = f"""
You are demonstrating Few-Shot Prompting.

Use the following examples as guidance for the
style and type of answer.

Example 1:

Task:
Explain Python.

Answer:
Python is a programming language used to create
software, applications, websites, and automation.

Example 2:

Task:
Explain a database.

Answer:
A database is a system used to store, organize,
and manage information.

Now perform the following task:

{task}
"""


            # -----------------------------
            # ROLE PROMPTING
            # -----------------------------

            elif technique == "Role Prompting":

                prompt = f"""
You are demonstrating Role Prompting.

Act as an experienced university teacher.

Explain the answer clearly and simply for a student.
Use an educational and professional tone.

Task:

{task}
"""


            # -----------------------------
            # STRUCTURED PROMPTING
            # -----------------------------

            else:

                prompt = f"""
You are demonstrating Structured Prompting.

Answer the task using exactly this structure:

1. Definition
2. Explanation
3. Practical Example
4. Key Points

Keep the answer clear and suitable for a university student.

Task:

{task}
"""

            response = generate_ai(prompt)

            if response.startswith("Gemini AI") or response.startswith("Unable"):
                error = response
            else:
                result = response

    return render_template(
        "prompt_lab.html",
        result=result,
        error=error,
        technique=technique,
        task=task
    )


# ==================================================
# START FLASK APPLICATION
# ==================================================

if __name__ == "__main__":
    app.run(port=5001, debug=True)