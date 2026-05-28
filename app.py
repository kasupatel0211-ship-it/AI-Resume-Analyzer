from fileinput import filename

from matplotlib.pyplot import text

from utils.resume_checker import is_resume

from utils.score_graph import generate_score_graph

from utils.chart_generator import generate_skill_chart

from flask import Flask, render_template, request, redirect, flash, session, send_file
import sqlite3
import os
from werkzeug.utils import secure_filename

from utils.pdf_reader import extract_text_from_pdf
from utils.skill_analyzer import detect_skills, missing_skills
from utils.scorer import calculate_score
from utils.job_matcher import match_job_role
from utils.suggestions import generate_suggestions

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.secret_key = "resume_analyzer_secret"

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ======================
# HOME
# ======================
@app.route('/')
def home():
    return render_template('index.html')

# ======================
# REGISTER
# ======================
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('database/resume.db')
        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                INSERT INTO users(name, email, password)
                VALUES (?, ?, ?)
                """,
                (name, email, password)
            )

            conn.commit()

            flash("Registration Successful!")
            return redirect('/login')

        except sqlite3.IntegrityError:

            flash("Email already exists!")

        finally:

            conn.close()

    return render_template('register.html')

# ======================
# LOGIN
# ======================
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('database/resume.db')
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM users
            WHERE email=? AND password=?
            """,
            (email, password)
        )

        user = cursor.fetchone()

        conn.close()

        if user:

            session['user_id'] = user[0]
            session['user_name'] = user[1]

            flash("Login Successful!")

            return redirect('/dashboard')

        else:

            flash("Invalid Email or Password")

    return render_template('login.html')


# ======================
# DASHBOARD
# ======================
@app.route('/dashboard')
def dashboard():

    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database/resume.db')
    cursor = conn.cursor()

    # Resume List
    cursor.execute(
        """
        SELECT * FROM resumes
        WHERE user_id=?
        ORDER BY id DESC
        """,
        (session['user_id'],)
    )

    resumes = cursor.fetchall()

    # Total Resumes
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM resumes
        WHERE user_id=?
        """,
        (session['user_id'],)
    )

    total_resumes = cursor.fetchone()[0]

    # Highest Score
    cursor.execute(
        """
        SELECT MAX(score)
        FROM resumes
        WHERE user_id=?
        """,
        (session['user_id'],)
    )

    highest_score = cursor.fetchone()[0]

    if highest_score is None:
        highest_score = 0

    # Average Score
    cursor.execute(
        """
        SELECT AVG(score)
        FROM resumes
        WHERE user_id=?
        """,
        (session['user_id'],)
    )

    average_score = cursor.fetchone()[0]

    if average_score is None:
        average_score = 0

    average_score = round(average_score)

    # Latest Role
    cursor.execute(
        """
        SELECT role
        FROM resumes
        WHERE user_id=?
        ORDER BY id DESC
        LIMIT 1
        """,
        (session['user_id'],)
    )

    role_data = cursor.fetchone()

    if role_data:
        latest_role = role_data[0]
    else:
        latest_role = "No Analysis Yet"

    # Score Trend Graph Data
    cursor.execute(
        """
        SELECT score
        FROM resumes
        WHERE user_id=?
        ORDER BY id
        """,
        (session['user_id'],)
    )

    score_rows = cursor.fetchall()

    scores = [row[0] for row in score_rows]

    graph_file = generate_score_graph(
        scores,
        session['user_id']
    )

    conn.close()

    return render_template(
        'dashboard.html',
        username=session['user_name'],
        resumes=resumes,
        total_resumes=total_resumes,
        highest_score=highest_score,
        average_score=average_score,
        latest_role=latest_role,
        graph_file=graph_file
    )

# ======================
# UPLOAD RESUME
# ======================
@app.route('/upload', methods=['GET', 'POST'])
def upload():

    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':

        file = request.files['resume']

        # No file selected
        if not file or file.filename == '':
            flash("Please select a file.")
            return redirect('/upload')

        # Only PDF allowed
        if not file.filename.lower().endswith('.pdf'):
            flash("Invalid file! Please upload a PDF resume.")
            return redirect('/upload')

        filename = secure_filename(file.filename)

        filepath = os.path.join(
            app.config['UPLOAD_FOLDER'],
            filename
        )

        file.save(filepath)

        # Extract PDF Text
        text = extract_text_from_pdf(filepath)
        
        print("PDF TEXT:")
        print(text[:1000])

        # Check Resume Validity
        if not is_resume(text):

            flash(
                "This file does not appear to be a resume. Please upload a valid resume PDF."
            )

            os.remove(filepath)

            return redirect('/upload')

        # Detect Skills
        skills = detect_skills(text)

        print("DETECTED SKILLS =", skills)

        # Missing Skills
        missing = missing_skills(skills)

        # Pie Chart
        chart_file = generate_skill_chart(
            skills,
            filename.replace(".pdf", "")
        )

        print("CHART FILE =", chart_file)

        # Score
        score = calculate_score(
            skills,
            text
        )

        # Job Role
        role = match_job_role(skills)

        # Suggestions
        suggestions = generate_suggestions(
            skills,
            text
        )

        conn = sqlite3.connect('database/resume.db')
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO resumes
            (user_id, file_name, score, role)
            VALUES (?, ?, ?, ?)
            """,
            (
                session['user_id'],
                filename,
                score,
                role
            )
        )

        conn.commit()
        conn.close()

        return render_template(
            'result.html',
            filename=filename,
            score=score,
            skills=skills,
            missing=missing,
            role=role,
            suggestions=suggestions,
            chart_file=chart_file
        )

    return render_template('upload.html')

# ======================
# HISTORY
# ======================
@app.route('/history')
def history():

    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database/resume.db')
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM resumes
        WHERE user_id=?
        ORDER BY id DESC
        """,
        (session['user_id'],)
    )

    resumes = cursor.fetchall()

    conn.close()

    return render_template(
        'history.html',
        resumes=resumes
    )
# ======================
# DOWNLOAD REPORT
# ======================
@app.route('/download-report/<filename>')
def download_report(filename):

    pdf_path = f"reports/{filename}.pdf"

    os.makedirs(
        "reports",
        exist_ok=True
    )

    conn = sqlite3.connect('database/resume.db')
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT score, role
        FROM resumes
        WHERE file_name=?
        ORDER BY id DESC
        LIMIT 1
        """,
        (filename,)
    )

    data = cursor.fetchone()

    conn.close()

    if data:

        score = data[0]
        role = data[1]

    else:

        score = 0
        role = "Not Found"

    # Resume PDF Path
    resume_path = os.path.join(
        "uploads",
        filename
    )

    # Extract Resume Text
    text = extract_text_from_pdf(
        resume_path
    )

    # AI Analysis
    skills = detect_skills(text)

    missing = missing_skills(skills)

    suggestions = generate_suggestions(
        skills,
        text
    )

    # Create PDF
    c = canvas.Canvas(
        pdf_path,
        pagesize=letter
    )

    y = 760

    # TITLE
    c.setFont("Helvetica-Bold", 24)

    c.drawString(
        120,
        y,
        "AI Resume Analysis Report"
    )

    y -= 40

    # Resume Info
    c.setFont("Helvetica-Bold", 16)

    c.drawString(
        50,
        y,
        "Resume Information"
    )

    y -= 30

    c.setFont("Helvetica", 12)

    c.drawString(
        70,
        y,
        f"File Name: {filename}"
    )

    y -= 20

    c.drawString(
        70,
        y,
        f"Resume Score: {score}%"
    )

    y -= 20

    c.drawString(
        70,
        y,
        f"Recommended Role: {role}"
    )

    y -= 40

    # Skills
    c.setFont("Helvetica-Bold", 16)

    c.drawString(
        50,
        y,
        "Detected Skills"
    )

    y -= 30

    c.setFont("Helvetica", 12)

    for skill in skills:

        c.drawString(
            70,
            y,
            f"• {skill}"
        )

        y -= 20

    y -= 20

    # Missing Skills
    c.setFont("Helvetica-Bold", 16)

    c.drawString(
        50,
        y,
        "Missing Skills"
    )

    y -= 30

    c.setFont("Helvetica", 12)

    for skill in missing[:5]:

        c.drawString(
            70,
            y,
            f"• {skill}"
        )

        y -= 20

    y -= 20

    # Suggestions
    c.setFont("Helvetica-Bold", 16)

    c.drawString(
        50,
        y,
        "Suggestions"
    )

    y -= 30

    c.setFont("Helvetica", 12)

    for item in suggestions:

        c.drawString(
            70,
            y,
            f"• {item}"
        )

        y -= 20

    y -= 30

    # Footer
    c.line(50, 80, 550, 80)

    c.setFont("Helvetica-Oblique", 11)

    c.drawString(
        170,
        50,
        "Generated By AI Resume Analyzer"
    )

    c.save()

    return send_file(
        pdf_path,
        as_attachment=True
    )

# ======================
# ADMIN PANEL
# ======================
@app.route('/admin')
def admin():

    # User must login
    if 'user_id' not in session:
        return redirect('/login')

    # Only admin email allowed
    conn = sqlite3.connect('database/resume.db')
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT email
        FROM users
        WHERE id=?
        """,
        (session['user_id'],)
    )

    user = cursor.fetchone()

    if not user or user[0] != "admin@gmail.com":

        conn.close()

        return "<h2 style='color:red;text-align:center;margin-top:50px;'>Access Denied</h2>"

    # Continue Admin Panel

    conn = sqlite3.connect('database/resume.db')
    cursor = conn.cursor()

    # Total Users
    cursor.execute(
        "SELECT COUNT(*) FROM users"
    )

    total_users = cursor.fetchone()[0]

    # Total Resumes
    cursor.execute(
        "SELECT COUNT(*) FROM resumes"
    )

    total_resumes = cursor.fetchone()[0]

    # Average Score
    cursor.execute(
        "SELECT AVG(score) FROM resumes"
    )

    avg_score = cursor.fetchone()[0]

    if avg_score is None:
        avg_score = 0

    avg_score = round(avg_score)

    # Get All Resume File Names
    cursor.execute(
        "SELECT file_name FROM resumes"
    )

    files = cursor.fetchall()

    conn.close()

    # Top Skills Calculation
    all_skills = []

    for file in files:

        filename = file[0]

        path = os.path.join(
            "uploads",
            filename
        )

        if os.path.exists(path):

            text = extract_text_from_pdf(path)

            skills = detect_skills(text)

            all_skills.extend(skills)

    # Skill Frequency
    skill_count = {}

    for skill in all_skills:

        if skill in skill_count:
            skill_count[skill] += 1
        else:
            skill_count[skill] = 1

    top_skills = sorted(
        skill_count.items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]

    return render_template(
        'admin.html',
        total_users=total_users,
        total_resumes=total_resumes,
        avg_score=avg_score,
        top_skills=top_skills
    )       
# ======================
# LOGOUT
# ======================
@app.route('/logout')
def logout():

    session.clear()

    flash("Logged Out Successfully")

    return redirect('/login')

# ======================
# MAIN
# ======================
if __name__ == '__main__':
    app.run(debug=True)