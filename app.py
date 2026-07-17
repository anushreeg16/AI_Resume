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
# Skill Weights
# ==========================

SKILL_WEIGHTS = {

    "python":12,
    "java":10,
    "c++":8,

    "sql":8,
    "mysql":6,

    "flask":8,
    "django":8,

    "html":3,
    "css":3,

    "javascript":5,

    "react":6,
    "node":6,

    "git":4,
    "github":4,

    "machine learning":15,
    "deep learning":15,

    "tensorflow":12,

    "pandas":8,
    "numpy":8,

    "opencv":10,

    "docker":6,
    "aws":8,

    "data structures":10,
    "algorithms":10,

    "communication":4,
    "problem solving":5

}




# ==========================
# Job Roles Database
# ==========================

JOB_ROLES = {


"ai engineer":
"""
Python
Machine Learning
Deep Learning
TensorFlow
Flask
SQL
Git
AWS
Communication
Problem Solving
""",



"python developer":
"""
Python
Flask
Django
SQL
HTML
CSS
JavaScript
Git
GitHub
""",



"java developer":
"""
Java
SQL
MySQL
Git
GitHub
Data Structures
Algorithms
Communication
""",



"full stack developer":
"""
HTML
CSS
JavaScript
React
Node
SQL
Git
GitHub
""",



"data scientist":
"""
Python
Pandas
NumPy
Machine Learning
Deep Learning
TensorFlow
SQL
Communication
"""


}




# ==========================
# Extract PDF Text
# ==========================

def extract_text(pdf_path):

    text=""

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
# Find Skills
# ==========================

def find_skills(text):

    detected=[]

    text=text.lower()


    for skill in SKILLS:

        pattern = r"\b" + re.escape(skill) + r"\b"


        if re.search(pattern,text):

            detected.append(skill)


    return detected





# ==========================
# ATS Score
# ==========================

def calculate_score(resume_text, job_description):


    resume_skills=find_skills(resume_text)

    job_skills=find_skills(job_description)


    if not job_skills:

        return 0



    total_weight=0

    matched_weight=0



    for skill in job_skills:


        weight=SKILL_WEIGHTS.get(skill,5)

        total_weight += weight



        if skill in resume_skills:

            matched_weight += weight



    score=round(
        (matched_weight/total_weight)*100
    )


    return min(score,100)





# ==========================
# Status
# ==========================

def score_status(score):

    if score>=80:

        return "Excellent"

    elif score>=60:

        return "Good"

    elif score>=40:

        return "Average"

    else:

        return "Low"





# ==========================
# Missing Skills
# ==========================

def missing_skills(resume_skills,job_skills):


    missing=[]


    for skill in job_skills:


        if skill not in resume_skills:

            missing.append(skill)


    return missing





# ==========================
# Feedback
# ==========================

def generate_feedback(score,skills,missing):


    feedback=[]


    if score>=80:

        feedback.append(
            "Excellent ATS compatibility."
        )


    elif score>=60:

        feedback.append(
            "Good resume with minor improvements."
        )


    else:

        feedback.append(
            "Resume needs improvement."
        )



    if len(skills)>=8:

        feedback.append(
            "Strong technical profile."
        )


    elif len(skills)>=4:

        feedback.append(
            "Moderate technical profile."
        )


    else:

        feedback.append(
            "Add more technical skills."
        )



    if missing:

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
# Main Route
# ==========================

@app.route("/",methods=["GET","POST"])

def index():


    if request.method=="POST":


        job_role=request.form.get(
            "job_role",
            ""
        ).strip()



        job_description=request.form.get(
            "job_description",
            ""
        ).strip()



        if not job_description and job_role:


            job_description=JOB_ROLES.get(
                job_role.lower(),
                ""
            )



        if not job_description:


            return render_template(
                "index.html",
                error="Please enter a valid Job Role or Job Description."
            )




        files=request.files.getlist(
            "resume"
        )



        results=[]



        job_skill_list=find_skills(
            job_description
        )



        for file in files:



            if file.filename=="":

                continue



            filepath=os.path.join(
                app.config["UPLOAD_FOLDER"],
                file.filename
            )



            file.save(filepath)



            resume_text=extract_text(
                filepath
            )



            skills=find_skills(
                resume_text
            )



            score=calculate_score(
                resume_text,
                job_description
            )



            missing=missing_skills(
                skills,
                job_skill_list
            )



            feedback=generate_feedback(
                score,
                skills,
                missing
            )



            results.append({

                "name":file.filename,

                "score":score,

                "status":score_status(score),

                "skills":skills,

                "missing":missing,

                "feedback":feedback

            })




        results=sorted(
            results,
            key=lambda x:x["score"],
            reverse=True
        )



        return render_template(
            "result.html",
            results=results
        )



    return render_template(
        "index.html"
    )





if __name__=="__main__":

    app.run(debug=True)