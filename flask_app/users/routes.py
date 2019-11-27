from flask import render_template, current_app, url_for, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required

from flask_app import db, bcrypt
from flask_app.models import User, UserGIFs
from flask_app.users.forms import RegistrationForm, LoginForm

users = Blueprint("users", __name__)

@users.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        current_app.logger.info("User is authenticated. Redirect to main page.")
        return redirect(url_for("main.index"))

    form = RegistrationForm()

    if form.validate_on_submit():
        current_app.logger.info("POST Request hit at /register and form has been validated")
        current_app.logger.info("Hashing password...")

        hashed = bcrypt.generate_password_hash(form.password.data).decode("utf-8")

        current_app.logger.info("Creating new user")

        user = User(username=form.username.data, password=hashed)

        current_app.logger.info("Adding new user to database")

        db.session.add(user)
        db.session.commit()

        current_app.logger.info("User has been added. Redirect to login page.")

        return redirect(url_for("users.login"))

    return render_template("register.html", title="Register", form=form)

@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        current_app.logger.info("User is authenticated. Redirect to main page.")

        return redirect(url_for("main.index"))

    form = LoginForm()

    if form.validate_on_submit():
        current_app.logger.info("POST Request hit at /login and form has been validated")
        current_app.logger.info("Checking password...")

        user = User.query.filter_by(username=form.username.data).first()

        if user is not None and bcrypt.check_password_hash(
            user.password, form.password.data
        ):
            login_user(user)
            return redirect(url_for("users.account"))

    return render_template("login.html", title="Login", form=form)

@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.index"))

@users.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = UpdateInterestsForm()

    if form.validate_on_submit():
        current_app.logger.info("POST Request hit at /account and form has been validated")
        
        current_app.logger.info("Updating username...")

        current_user.username = form.username.data

        db.session.commit()

        return redirect(url_for("users.account"))

    elif request.method == "GET":
        logger.info("GET Request hit at /account")
        form.username.data = current_user.username

    return render_template("account.html", title="Account", form=form)
