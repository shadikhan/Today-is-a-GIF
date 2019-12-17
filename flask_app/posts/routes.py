from flask import render_template, request, current_app, Blueprint, redirect, url_for

from flask_app import db
from flask_app.models import GIFPost
from flask_app.posts.forms import CreatePostForm

posts = Blueprint("posts", __name__)
main = Blueprint("main", __name__)

@posts.route("/create_post", methods=["GET", "POST"])
def create_post():
    form = CreatePostForm()

    if form.validate_on_submit():
        gifPost = GIFPost(
            title = form.title.data,
            link = form.link.data
        )

        db.session.add(gifPost)
        db.session.commit()

        return redirect(url_for("main.index"))

    return render_template(
        "createGIFPost.html", title="Create GIF POST!", form=form
    )
