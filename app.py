from flask import Flask, render_template, request
import os
import re
import pdfplumber

app = Flask(__name__)
app.secret_key = "resumeai123"

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ==========================
# Skill Database
# ==========================

SKILLS = [
    "python",
    "java",
    "c++",
    "sql",
    "mysql",
    "flask",
    "django",
    "html",
    "css",
    "javascript",
    "react",
    "node",
    "git",
    "github",
    "machine learning",
    "deep learning",
    "tensorflow",
    "pandas",
    "numpy",
    "opencv",
    "docker",
    "aws",
    "data structures",
    "algorithms",
    "communication",
    "problem solving"
]


# ==========================
# PDF Text Extraction
# ==========================

def extract_text(pdf_path):

    text = ""

    try:

        with pdfplumber.open(pdf_path) as pdf:

            for page in pdf.pages:

                page_text = page.extract_text()

                if page_text:
                    text += page_text.lower()

    except Exception:
        pass

    return text


# ==========================
# Skill Detection
# ==========================

def find_skills(text):

    detected = []

    text = text.lower()

    for skill in SKILLS:

        if skill.lower() in text:
            detected.append(skill)

    return detected


# ==========================
# ATS Score
# ==========================

def calculate_score(resume_text, job_description):

    resume_words = set(
        re.findall(r"\w+", resume_text.lower())
    )

    job_words = set(
        re.findall(r"\w+", job_description.lower())
    )

    if len(job_words) == 0:
        return 0

    matched = resume_words.intersection(job_words)

    score = int(
        (len(matched) / len(job_words)) * 100
    )

    if score > 100:
        score = 100

    return score


# ==========================
# Score Status
# ==========================

def score_status(score):

    if score >= 80:
        return "Excellent"

    elif score >= 60:
        return "Good"

    elif score >= 40:
        return "Average"

    else:
        return "Low"


# ==========================
# Missing Skills
# ==========================

def missing_skills(resume_skills, job_skills):

    missing = []

    for skill in job_skills:

        if skill not in resume_skills:
            missing.append(skill)

    return missing


# ==========================
# AI Feedback
# ==========================

def generate_feedback(score, skills, missing):

    feedback = []

    if score >= 80:

        feedback.append(
            "Excellent ATS compatibility."
        )

    elif score >= 60:

        feedback.append(
            "Good resume with minor improvements required."
        )

    else:

        feedback.append(
            "Resume needs significant improvement."
        )

    if len(skills) >= 8:

        feedback.append(
            "Strong technical profile."
        )

    elif len(skills) >= 4:

        feedback.append(
            "Moderate technical profile."
        )

    else:

        feedback.append(
            "Add more technical skills."
        )

    if len(missing):

        feedback.append(
            "Recommended Skills: "
            + ", ".join(missing)
        )

    else:

        feedback.append(
            "No major skill gaps detected."
        )

    return feedback
# ==========================
# Home Route
# ==========================

@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":

        job_description = request.form.get(
            "job_description",
            ""
        )

        files = request.files.getlist("resume")

        results = []

        job_skill_list = find_skills(
            job_description
        )

        for file in files:

            if file.filename == "":
                continue

            filepath = os.path.join(
                app.config["UPLOAD_FOLDER"],
                file.filename
            )

            file.save(filepath)

            resume_text = extract_text(
                filepath
            )

            skills = find_skills(
                resume_text
            )

            score = calculate_score(
                resume_text,
                job_description
            )

            missing = missing_skills(
                skills,
                job_skill_list
            )

            feedback = generate_feedback(
                score,
                skills,
                missing
            )

            results.append({

                "name": file.filename,

                "score": score,

                "status": score_status(score),

                "skills": skills,

                "missing": missing,

                "feedback": feedback

            })

        # Candidate Ranking
        results = sorted(
            results,
            key=lambda x: x["score"],
            reverse=True
        )

        return render_template(
            "result.html",
            results=results
        )

    return render_template(
        "index.html"
    )


# ==========================
# Run Flask App
# ==========================

if __name__ == "__main__":

    app.run(
        debug=True
    )