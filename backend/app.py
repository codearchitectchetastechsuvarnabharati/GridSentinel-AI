from flask import Flask, render_template, request, redirect, session, jsonify
import os
import pandas as pd
from datetime import datetime
from tempfile import NamedTemporaryFile


from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from flask import send_file

from constants import APP_NAME, APP_TAGLINE, PLATFORM_VERSION, FOOTER_TEXT
from auth_utils import validate_or_register_user
from smart_meter_ai import run_smart_meter_ai_pipeline
from db_backup import init_db, get_connection

from constants import APP_NAME, APP_TAGLINE, PLATFORM_VERSION, FOOTER_TEXT
from auth_utils import validate_or_register_user
from smart_meter_ai import run_smart_meter_ai_pipeline

# -------------------------------------------------
# PATH CONFIGURATION
# -------------------------------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
DATA_DIR = os.path.join(BASE_DIR, "data")
CSV_DIR = os.path.join(DATA_DIR, "csv_inputs")
AUDIT_FILE = os.path.join(DATA_DIR, "audit_log.xlsx")
USERS_FILE = os.path.join(DATA_DIR, "users.xlsx")

# -------------------------------------------------
# FLASK APP
# -------------------------------------------------
app = Flask(
    __name__,
    template_folder=TEMPLATES_DIR
)
app.secret_key = "bescom_internal_only"

# -------------------------------------------------
# SAFE AUDIT LOGGING (WINDOWS-SAFE)
# -------------------------------------------------
def audit(user, action):
    os.makedirs(DATA_DIR, exist_ok=True)

    row = {
        "timestamp": datetime.now(),
        "user": user,
        "action": action
    }

    if os.path.exists(AUDIT_FILE):
        df = pd.read_excel(AUDIT_FILE)
    else:
        df = pd.DataFrame(columns=row.keys())

    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)

    # ✅ Atomic write (prevents PermissionError)
    with NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        temp_path = tmp.name

    df.to_excel(temp_path, index=False)
    os.replace(temp_path, AUDIT_FILE)

# -------------------------------------------------
# REGISTER
# -------------------------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = request.form.get("username")

        if not user or "@" not in user:
            return "Invalid email", 400

        if user.endswith("@bescom.in"):
            role = "admin"
        elif user.endswith("@bescom.co.in"):
            role = "engineer"
        else:
            return "Only BESCOM users allowed", 403

        session["user"] = user
        session["role"] = role

        return redirect("/dashboard")

    return render_template("register.html")
# -------------------------------------------------
# LOGIN
# -------------------------------------------------
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method=="POST":
        user=request.form["username"]
    # VALIDATE USER
        role,err =validate_or_register_user(user)
        if err:
            return"unauthorized BESCOM user",403
        # STORE SESSION
        session["user"]=user
        session["role"]=role
        # SAVE IN DB
        conn=get_connection()
        cur=conn.cursor()
        cur.execute(
    "INSERT INTO users_backup (username, role, timestamp) VALUES (?, ?, datetime('now'))",
    (user, role)
)
        conn.commit()
        conn.close()

        # AUDIT LOG
        audit(user,"LOGIN")

        return redirect("/dashboard")
    return render_template(
        "login.html",
        app_name=APP_NAME,
        tagline=APP_TAGLINE,
        version=PLATFORM_VERSION,
        footer=FOOTER_TEXT
    )

# -------------------------------------------------
# DASHBOARD
# -------------------------------------------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    csv_files = [
        os.path.join(CSV_DIR, f)
        for f in os.listdir(CSV_DIR)
        if f.endswith(".csv")
    ]

    if not csv_files:
        return "No CSV files found in data/csv_inputs", 500

    latest_csv = max(csv_files, key=os.path.getmtime)

    zones, inspections = run_smart_meter_ai_pipeline(latest_csv)
    audit(session["user"], "VIEW_DASHBOARD")

    return render_template(
        "dashboard.html",
        app_name=APP_NAME,
        tagline=APP_TAGLINE,
        version=PLATFORM_VERSION,
        footer=FOOTER_TEXT,
        zones=zones,
        inspections=inspections
    )

# -------------------------------------------------
# CHART DATA API (CONFIDENCE BANDS)
# -------------------------------------------------
@app.route("/api/chart-data")
def chart_data():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 403

    csv_files = [
        os.path.join(CSV_DIR, f)
        for f in os.listdir(CSV_DIR)
        if f.endswith(".csv")
    ]

    latest_csv = max(csv_files, key=os.path.getmtime)
    zones, _ = run_smart_meter_ai_pipeline(latest_csv)

    return jsonify({
        "zones": zones["zone_id"].tolist(),
        "forecast": zones["forecast_load"].tolist(),
        "peak": zones["historical_peak"].tolist(),
        "upper": (zones["forecast_load"] * 1.1).round(2).tolist(),
        "lower": (zones["forecast_load"] * 0.9).round(2).tolist()
    })

# -------------------------------------------------
# CHARTS PAGE
# -------------------------------------------------
@app.route("/charts")
def charts():
    if "user" not in session:
        return redirect("/login")

    audit(session["user"], "VIEW_CHARTS")

    return render_template(
        "charts.html",
        app_name=APP_NAME,
        version=PLATFORM_VERSION,
        footer=FOOTER_TEXT
    )

# -------------------------------------------------
# EXPORT
# -------------------------------------------------

@app.route("/export")
def export():

    if "user" not in session:
        return redirect("/login")

    # ✅ Get latest CSV
    csv_files = [
        os.path.join(CSV_DIR, f)
        for f in os.listdir(CSV_DIR)
        if f.endswith(".csv")
    ]

    if not csv_files:
        return "No CSV data available", 500

    latest_csv = max(csv_files, key=os.path.getmtime)

    zones, inspections = run_smart_meter_ai_pipeline(latest_csv)

    # ✅ Create PDF file
    pdf_path = os.path.join(BASE_DIR, "data", "report.pdf")

    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

    y = height - 40

    # ✅ Title
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "GridSentinel AI Report")
    y -= 30

    # ✅ Zones Section
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Zones Summary")
    y -= 20

    c.setFont("Helvetica", 10)

    for _, row in zones.iterrows():
        text = f"Zone: {row.get('zone_id', '')} | Load: {row.get('forecast_load', '')} | Risk: {row.get('risk_level', '')}"
        c.drawString(50, y, text)
        y -= 15

        if y < 50:
            c.showPage()
            y = height - 40

    # ✅ Page break
    c.showPage()
    y = height - 40

    # ✅ Inspections Section
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Inspection Alerts")
    y -= 20

    c.setFont("Helvetica", 10)

    for _, row in inspections.iterrows():
        text = f"Meter: {row.get('meter_id', '')} | Score: {row.get('anomaly_score', '')}"
        c.drawString(50, y, text)
        y -= 15

        if y < 50:
            c.showPage()
            y = height - 40

    # ✅ Save PDF
    c.save()

    return send_file(pdf_path, as_attachment=True)
# -------------------------------------------------
# ✅ ADMIN PAGE
# -------------------------------------------------
@app.route("/admin")
def admin():
    if "user" not in session:
        return redirect("/login")
    # ONLY ADMIN ALLOWED
    if session.get("role")!="admin":
        return "Access Denied",403

    users_df = pd.read_excel(USERS_FILE) if os.path.exists(USERS_FILE) else pd.DataFrame()
    audit_df = pd.read_excel(AUDIT_FILE) if os.path.exists(AUDIT_FILE) else pd.DataFrame()

    audit(session["user"], "VIEW_ADMIN")

    return render_template(
        "admin.html",
        app_name=APP_NAME,
        version=PLATFORM_VERSION,
        footer=FOOTER_TEXT,
        users=users_df,
        audit=audit_df
    )
# -------------------------------------------------
# ✅ CLEAR LOGS
# -------------------------------------------------
@app.route("/clear-logs")
def clear_logs():

    if "user" not in session or session.get("role", "").lower() != "admin":
        return "Access Denied", 403

    if not os.path.exists(AUDIT_FILE):
        return redirect("/admin")

    df = pd.read_excel(AUDIT_FILE)

    # ✅ Keep only latest half
    half_index = len(df) // 2
    df = df.iloc[half_index:]

    df.to_excel(AUDIT_FILE, index=False)

    return redirect("/admin")

# ============================================================
# PROFILE PAGE
# ============================================================

@app.route("/profile")
def profile():
    if "user" not in session:
        return redirect("/login")

    return render_template(
        "profile.html",
        app_name=APP_NAME,
        version=PLATFORM_VERSION,
        footer=FOOTER_TEXT,
        user=session.get("user")
    )

# -------------------------------------------------
# LOGOUT
# -------------------------------------------------
@app.route("/logout")
def logout():
    if "user" in session:
        audit(session["user"], "LOGOUT")

    session.clear()
    return redirect("/login")

# -------------------------------------------------
# RUN SERVER
# -------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
