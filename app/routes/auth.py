from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)
from flask_login import login_user, logout_user, login_required

from app import db
from app.models.user import User


auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not username or not email or not password:
            flash("All fields are required.", "error")
            return render_template("auth/register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return render_template("auth/register.html")

        if password != confirm:
            flash("Passwords do not match.", "error")
            return render_template("auth/register.html")

        if User.query.filter(
            (User.username == username) | (User.email == email)
        ).first():
            flash("Username or email is already registered.", "error")
            return render_template("auth/register.html")

        user = User(username=username, email=email)
        user.set_password(password)

        db.session.add(user)

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash("Registration failed. Please try again.", "error")
            return render_template("auth/register.html")

        login_user(user)

        flash(f"Welcome to DreamCareer, {username}!", "success")

        return redirect(url_for("main.home"))

    return render_template("auth/register.html")


@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        identifier = request.form.get("identifier", "").strip()

        password = request.form.get("password", "")

        user = User.query.filter(
            (User.username == identifier)
            | (User.email == identifier.lower())
        ).first()

        if not user or not user.check_password(password):
            flash("Invalid credentials. Please try again.", "error")
            return render_template("auth/login.html")

        login_user(user)

        flash(f"Welcome back, {user.username}!", "success")

        return redirect(url_for("main.home"))

    return render_template("auth/login.html")


@auth.route("/logout", methods=["POST"])
@login_required
def logout():

    logout_user()

    flash("You have been logged out.", "success")

    return redirect(url_for("main.home"))
