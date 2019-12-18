from flask import render_template, current_app, url_for, redirect, request, Blueprint, session
from flask_login import login_user, current_user, logout_user, login_required

from flask_app import db, bcrypt
from flask_app.models import User, UserGIF
from flask_app.users.forms import RegistrationForm, LoginForm, UpdateInterestsForm
from flask_app.giphyUtils import getGIFs
from datetime import datetime

import qrcode
import qrcode.image.svg as svg

from io import BytesIO

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

        user = User(
            username=form.username.data, 
            password=hashed, 
            interest1=form.firstInterest.data, 
            interest2=form.secondInterest.data,
            interest3=form.thirdInterest.data
            )

        current_app.logger.info("Adding new user to database")
        db.session.add(user)
        db.session.commit()

        current_app.logger.info("Getting GIFS for User {user.username}")
        firstInterestGIFs = getGIFs(user.interest1)
        for url in firstInterestGIFs:
            userGIF = UserGIF(link = url, user = user)
            db.session.add(userGIF)
        

        secondInterestGIFs = getGIFs(user.interest2)
        for url in secondInterestGIFs:
            userGIF = UserGIF(link = url, user = user)
            db.session.add(userGIF)

        thirdInterestGIFs = getGIFs(user.interest3)
        for url in thirdInterestGIFs:
            userGIF = UserGIF(link = url, user = user)
            db.session.add(userGIF)
        db.session.commit()

        current_app.logger.info("User has been added, as well as their GIF Interests. Redirect to login page.")

        #return redirect(url_for("users.login"))
        session['reg_username'] = user.username

        return redirect(url_for('users.tfa'))

    return render_template("register.html", title="Register", form=form)

@users.route("/tfa")
def tfa():
    if 'reg_username' not in session:
        return redirect(url_for('main.index'))

    headers = {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0' # Expire immediately, so browser has to reverify everytime
    }

    return render_template('tfa.html'), headers

@users.route("/qr_code")
def qr_code():
    if 'reg_username' not in session:
        return redirect(url_for('main.index'))
    
    user = User.query.filter_by(username=session['reg_username']).first()

    session.pop('reg_username')

    img = qrcode.make(user.get_auth_uri(), image_factory=svg.SvgPathImage)

    stream = BytesIO()

    img.save(stream)

    headers = {
        'Content-Type': 'image/svg+xml',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0' # Expire immediately, so browser has to reverify everytime
    }

    return stream.getvalue(), headers

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
            current_app.logger.info("Logging in user...")
            login_user(user)

            current_app.logger.info("User logged in")

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
        current_app.logger.info("Updating Interests...")

        current_user.interest1 = form.firstInterest.data
        current_user.interest2 = form.secondInterest.data
        current_user.interest3 = form.thirdInterest.data
        current_user.lastUpdated = datetime.now()
        updateUserGIFs()

        return redirect(url_for("users.account"))

    elif request.method == "GET":
        current_app.logger.info("GET Request hit at /account")
        form.firstInterest.data = current_user.interest1
        form.secondInterest.data = current_user.interest2
        form.thirdInterest.data = current_user.interest3

    return render_template("account.html", title="Account", form=form)

@users.route("/userFeed")
@login_required
def userFeed():
    current_app.logger.info("GET Request hit at /userFeed")
    lastUpdatedTime = current_user.lastUpdated
    timeDifference = datetime.now() - lastUpdatedTime
            
    hoursSinceUpdate = divmod(timeDifference.total_seconds(), 3600)[0]
    current_app.logger.info(f"User profile last updated {hoursSinceUpdate} hours ago")

    # minutesSinceUpdate = divmod(timeDifference.total_seconds(), 60)[0]
    # current_app.logger.info(f"User profile last updated {minutesSinceUpdate} minutes ago")

    if hoursSinceUpdate >= 24:
        current_app.logger.info(f"User profile last updated at least 24 hours ago, so update their GIFs")
        updateUserGIFs()
    
    userGIFs = UserGIF.query.filter_by(user = current_user).all()
    userGIFs = map(lambda x : x.link, userGIFs)
    return render_template("userFeed.html", title = "Daily GIFs Feed", userGIFs = userGIFs)
        

def updateUserGIFs():
    firstInterestGIFs = getGIFs(current_user.interest1)
    secondInterestGIFs = getGIFs(current_user.interest2)
    thirdInterestGIFs = getGIFs(current_user.interest3)
    gifs = firstInterestGIFs + secondInterestGIFs + thirdInterestGIFs

    i = 0
    userGIFs = UserGIF.query.filter_by(user = current_user).all()
    for c in userGIFs:
        c.link = gifs[i]
        i += 1

    current_user.lastUpdated = datetime.now()
    db.session.commit()
    

    


