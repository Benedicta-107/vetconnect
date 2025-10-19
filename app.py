# app.py
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from extensions import db, migrate, mail
from models import User, Appointment, Message
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")  # or your vet.env path

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///database/vetconnect.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS", "False") == "True"
    

    app.config.update(
        MAIL_SERVER=os.environ.get("MAIL_SERVER", "smtp.gmail.com"),
        MAIL_PORT=int(os.environ.get("MAIL_PORT", 587)),
        MAIL_USE_TLS=os.environ.get("MAIL_USE_TLS", "1") in ("1", "true", "True"),
        MAIL_USERNAME=os.environ.get("MAIL_USERNAME"),
        MAIL_PASSWORD=os.environ.get("MAIL_PASSWORD"),
        MAIL_DEFAULT_SENDER=os.environ.get("MAIL_DEFAULT_SENDER"),
        MAIL_SUPPRESS_SEND=False,
    )

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])

    # ------------ helpers ------------
    def send_email(to, subject, html):
        from flask_mail import Message
        try:
            msg = Message(subject, recipients=[to], html=html)
            mail.send(msg)
        except Exception as e:
            app.logger.warning(f"Email send failed: {e}")

    def login_required(f):
        from functools import wraps
        from urllib.parse import urlparse
        @wraps(f)
        def wrapper(*args, **kwargs):
            if "user_id" not in session:
                flash("Please log in to continue.", "warning")
                return redirect(url_for("login", next=request.path))
            return f(*args, **kwargs)
        return wrapper

    def admin_required(f):
        from functools import wraps
        @wraps(f)
        def wrapper(*args, **kwargs):
            if "user_id" not in session:
                flash("Please log in to continue.", "warning")
                return redirect(url_for("login"))
            user = db.session.get(User, session["user_id"])
            if not user or not user.is_admin:
                flash("Admin access required.", "danger")
                return redirect(url_for("home"))
            return f(*args, **kwargs)
        return wrapper

    # ------------ routes ------------
    @app.route("/")
    def home():
        appts = []
        if session.get("user_id"):
            appts = (
                db.session.query(Appointment)
                .filter_by(user_id=session["user_id"])
                .order_by(Appointment.date, Appointment.time)
                .limit(5)
                .all()
            )
        return render_template("home.html", appts=appts)

    @app.route("/dashboard")
    @login_required
    def dashboard():
        appts = (
            db.session.query(Appointment)
            .filter_by(user_id=session["user_id"], hidden_by_user=False)
            .order_by(Appointment.date, Appointment.time)
            .all()
        )
        return render_template("dashboard.html", appts=appts)

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            name = request.form.get("name","").strip()
            email = request.form.get("email","").strip().lower()
            password = request.form.get("password","")
            confirm = request.form.get("confirm","")

            if not name or not email or not password:
                flash("All fields are required.", "warning")
                return redirect(url_for("register"))
            if password != confirm:
                flash("Passwords do not match.", "danger")
                return redirect(url_for("register"))

            if db.session.query(User).filter_by(email=email).first():
                flash("Email already registered.", "danger")
                return redirect(url_for("register"))

            user = User(
                name=name,
                email=email,
                password_hash=generate_password_hash(password),
                is_admin=False,
            )
            db.session.add(user)
            db.session.commit()
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("login"))

        return render_template("register.html")

    @app.route("/login", methods=["GET","POST"])
    def login():
        #pull the ?next=/book param
        next_url = request.args.get("next", "")
        if request.method == "POST":
            email = request.form.get("email","").strip().lower()
            password = request.form.get("password","")
            user = db.session.query(User).filter_by(email=email).first()
            if not user or not check_password_hash(user.password_hash, password):
                flash("Invalid email or password.", "danger")
                return redirect(url_for("login", next=next_url))
            session["user_id"] = user.id
            session["user_name"] = user.name
            session["is_admin"] = bool(user.is_admin)
            flash(f"Welcome, {user.name}!", "success")
            if next_url and urlparse(next_url).path.startswith("/"):
                return redirect(next_url)
            return redirect(url_for("home"))
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        flash("Logged out.", "info")
        return redirect(url_for("home"))

    @app.route("/book", methods=["GET","POST"])
    @login_required
    def book():
        if request.method == "POST":
            pet_name = request.form.get("pet_name","").strip()
            service  = request.form.get("service","").strip()
            date     = request.form.get("date","").strip()
            time     = request.form.get("time","").strip()
            if not (pet_name and service and date and time):
                flash("Please complete all fields.", "warning")
                return redirect(url_for("book"))

            appt = Appointment(
                user_id=session["user_id"],
                pet_name=pet_name,
                service=service,
                date=date,
                time=time,
            )
            db.session.add(appt)
            db.session.commit()

            user = db.session.get(User, session["user_id"])
            if user and user.email:
                send_email(
                    to=user.email,
                    subject="Your Peaceland Vet appointment request",
                    html=f"""
                        <p>Hi {user.name},</p>
                        <p>Thanks! We received your request for <b>{service}</b> on <b>{date}</b> at <b>{time}</b> for <b>{pet_name or 'your pet'}</b>.</p>
                        <p>We’ll confirm shortly.</p>
                        <p>— Peaceland Veterinary Services</p>
                    """,
                )

            for admin in [e.strip() for e in os.environ.get("ADMIN_EMAILS","").split(",") if e.strip()]:
                send_email(
                    to=admin,
                    subject="New appointment request",
                    html=f"""
                        <p>New request from <b>{user.name}</b> ({user.email})</p>
                        <ul>
                          <li>Service: {service}</li>
                          <li>Date: {date}</li>
                          <li>Time: {time}</li>
                          <li>Pet: {pet_name or '-'}</li>
                        </ul>
                    """,
                )

            flash("Your appointment request was submitted. We'll confirm soon.", "success")
            return redirect(url_for("dashboard"))

        return render_template("book.html")

    @app.route("/contact", methods=["POST"])
    def contact():
        name = request.form.get("name","").strip()
        email = request.form.get("email","").strip()
        message = request.form.get("message","").strip()
        if not (name and email and message):
            flash("Please complete the contact form.", "warning")
            return redirect(url_for("home"))
        db.session.add(Message(name=name, email=email, message=message))
        db.session.commit()
        flash("Thanks! We’ll be in touch.", "success")
        return redirect(url_for("home"))

    @app.route("/admin", methods=["GET","POST"])
    @admin_required
    def admin():
        if request.method == "POST":
            action  = request.form.get("action")
            appt_id = request.form.get("appt_id", type=int)
            if action in ("confirm","cancel") and appt_id:
                appt = db.session.get(Appointment, appt_id)
                if appt:
                    appt.status = "confirmed" if action == "confirm" else "cancelled"
                    db.session.commit()

                    user = db.session.get(User, appt.user_id)
                    if user and user.email:
                        subject = f"VetConnect: Appointment {appt.status}"
                        body = (
                            f"<p>Hi {user.name},</p>"
                            f"<p>Your appointment has been <b>{appt.status}</b>:</p>"
                            f"<ul><li><b>Pet</b>: {appt.pet_name}</li>"
                            f"<li><b>Service</b>: {appt.service}</li>"
                            f"<li><b>Date</b>: {appt.date}</li>"
                            f"<li><b>Time</b>: {appt.time}</li></ul>"
                            f"<p>— Peaceland Veterinary Services</p>"
                        )
                        send_email(user.email, subject, body)
                flash(f"Appointment {appt_id} set to {action}ed.", "success")
                return redirect(url_for("admin"))

        status = request.args.get("status","").strip().lower()
        q      = request.args.get("q","").strip()
        date   = request.args.get("date","").strip()

        query = db.session.query(Appointment).join(User).filter(Appointment.hidden_by_admin == False)
        if status in ("pending","confirmed","cancelled"):
            query = query.filter(Appointment.status == status)
        if date:
            query = query.filter(Appointment.date == date)
        if q:
            like = f"%{q}%"
            query = query.filter(
                db.or_(User.name.ilike(like), Appointment.pet_name.ilike(like), Appointment.service.ilike(like))
            )
        appts = query.order_by(Appointment.date, Appointment.time, Appointment.status).all()
        msgs = db.session.query(Message).order_by(Message.submitted_at.desc()).all()
        return render_template("admin.html", appts=appts, msgs=msgs, status=status, q=q, date=date)

    @app.route("/make_admin/<email>")
    def make_admin(email):
        user = db.session.query(User).filter_by(email=email.lower()).first()
        if user:
            user.is_admin = True
            db.session.commit()
            flash(f"{email} is now admin.", "info")
        else:
            flash("User not found.", "warning")
        return redirect(url_for("home"))

    @app.route("/profile", methods=["GET","POST"])
    @login_required
    def profile():
        user = db.session.get(User, session["user_id"])
        if request.method == "POST":
            name  = request.form.get("name","").strip()
            email = request.form.get("email","").strip().lower()
            if not name or not email:
                flash("Name and email are required.", "warning")
                return redirect(url_for("profile"))

            new_pw = request.form.get("new_password","")
            cur_pw = request.form.get("current_password","")
            if new_pw:
                if not check_password_hash(user.password_hash, cur_pw):
                    flash("Current password is incorrect.", "danger")
                    return redirect(url_for("profile"))
                user.password_hash = generate_password_hash(new_pw)

            user.name = name
            user.email = email
            db.session.commit()

            session["user_name"] = user.name
            flash("Profile updated.", "success")
            return redirect(url_for("profile"))

        return render_template("profile.html", user=user)

    @app.post("/me/appointments/hide")
    @login_required
    def user_hide_appointment():
        appt_id = request.form.get("appt_id", type=int)
        appt = db.session.get(Appointment, appt_id)
        if appt and appt.user_id == session["user_id"]:
            appt.hidden_by_user = True
            db.session.commit()
            flash("Appointment hidden.", "info")
        return redirect(url_for("dashboard"))

    @app.post("/me/appointments/delete")
    @login_required
    def user_delete_appointment():
        appt_id = request.form.get("appt_id", type=int)
        appt = db.session.get(Appointment, appt_id)
        if appt and appt.user_id == session["user_id"]:
            db.session.delete(appt)
            db.session.commit()
            flash("Appointment deleted.", "success")
        return redirect(url_for("dashboard"))

    @app.post("/admin/appointments/archive")
    @admin_required
    def admin_archive_appointment():
        appt_id = request.form.get("appt_id", type=int)
        appt = db.session.get(Appointment, appt_id)
        if appt:
            appt.hidden_by_admin = True
            db.session.commit()
            flash(f"Appointment {appt_id} archived.", "success")
        return redirect(url_for("admin"))

    @app.post("/admin/appointments/unarchive")
    @admin_required
    def admin_unarchive_appointment():
        appt_id = request.form.get("appt_id", type=int)
        appt = db.session.get(Appointment, appt_id)
        if appt:
            appt.hidden_by_admin = False
            db.session.commit()
            flash(f"Appointment {appt_id} restored.", "success")
        return redirect(url_for("admin"))


    @app.post("/admin/appointments/delete")
    @admin_required
    def admin_delete_appointment():
        appt_id = request.form.get("appt_id", type=int)
        appt = db.session.get(Appointment, appt_id)
        if appt:
            db.session.delete(appt)
            db.session.commit()
            flash(f"Appointment {appt_id} deleted.", "success")
        return redirect(url_for("admin"))
        # ---------------- Password reset ----------------
    @app.route("/reset", methods=["GET", "POST"])
    def reset_request():
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            user = db.session.query(User).filter_by(email=email).first()
            # Always respond the same to avoid account enumeration
            flash("If that email exists, a reset link has been sent.", "info")
            if user:
                token = ts.dumps(email, salt="password-reset")
                link = url_for("reset_token", token=token, _external=True)
                send_email(
                    to=email,
                    subject="Reset your VetConnect password",
                    html=f"""
                        <p>We received a request to reset your password.</p>
                        <p><a href="{link}">Click here to reset your password</a></p>
                        <p>If you didn't request this, you can ignore this email.</p>
                    """,
                )
            return redirect(url_for("login"))
        return render_template("home.html")

    @app.route("/reset/<token>", methods=["GET", "POST"])
    def reset_token(token):
        # 1 hour expiry
        try:
            email = ts.loads(token, salt="password-reset", max_age=3600)
        except Exception:
            flash("That reset link is invalid or expired.", "danger")
            return redirect(url_for("reset_request"))

        user = db.session.query(User).filter_by(email=email).first()
        if not user:
            flash("Account not found.", "warning")
            return redirect(url_for("reset_request"))

        if request.method == "POST":
            pw1 = request.form.get("password", "")
            pw2 = request.form.get("confirm", "")
            if not pw1:
                flash("Password is required.", "warning")
                return redirect(request.url)
            if pw1 != pw2:
                flash("Passwords do not match.", "danger")
                return redirect(request.url)

            user.password_hash = generate_password_hash(pw1)
            db.session.commit()
            flash("Password updated. Please log in.", "success")
            return redirect(url_for("login"))

        return render_template("reset_token.html", email=email)

        # ---- one-off CLI: create tables without migrations ----
    @app.cli.command("create-db")
    def create_db_command():
        """Create tables directly without migrations."""
        from models import User, Appointment, Message  # make sure models are imported
        db.create_all()
        print("✅ All tables created successfully.")
    return app


# Support `flask run` directly
app = create_app()

    # ------------ one-off CLI: create tables without migrations ------------