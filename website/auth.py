from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from .models import User, Organization
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from website.forms import SignUpForm, LoginForm

auth = Blueprint("auth", __name__)


@auth.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=True)
                flash(f"Successfully logged in as {user.email}", category="success")
                return redirect(url_for("views.dashboard"))
            else:
                flash("Incorrect password.", category="danger")
        else:
            flash("User with that email does not exist.", category="danger")

    return render_template("login.html", form=form)


@auth.route('logout')
def logout():
    logout_user()
    flash("Logged out successfully.", category="info")
    return redirect(url_for("auth.login"))


@auth.route('/', methods=["GET", "POST"])
@auth.route('/sign-up', methods=["GET", "POST"])
def sign_up():
    form = SignUpForm()

    if form.validate_on_submit():
        organization = Organization.query.filter_by(name=form.organization.data).first()
        if not organization:
            organization = Organization(name=form.organization.data)
            db.session.add(organization)

        new_user = User(email=form.email.data,
                        first_name=form.first_name.data,
                        last_name=form.last_name.data,
                        role=form.role.data,
                        password=generate_password_hash(form.password1.data, method="sha256"))
        organization.team.append(new_user)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user, remember=True)
        flash(f"Account created successfully! You are now logged in as {new_user.email}", category="success")

        return redirect(url_for("views.dashboard"))

    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f"{err_msg}", category="danger")

    return render_template("sign_up.html", form=form)


@auth.route('/demo')
def demo():
    # Login as demo user if selected from login/sign-up page.
    demo_user = User.query.filter_by(email="test@email.com").first()
    login_user(demo_user, remember=True)
    flash(f"Successfully logged in as {demo_user.email}", category="success")
    return redirect(url_for("views.dashboard"))
