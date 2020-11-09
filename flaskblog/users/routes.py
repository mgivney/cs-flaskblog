from flask import Blueprint, url_for, flash, redirect, request, render_template
from flask_login import login_user, current_user
from flask_login.utils import login_required, logout_user
from flaskblog import bcrypt
from flaskblog.models import Post, User
from flaskblog.users.forms import (
    AccountForm, RegistrationForm, LoginForm,
    RequestResetForm, ResetPasswordForm)
from flaskblog.users.utils import save_picture, send_reset_email


users = Blueprint('users', __name__)


@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        u = User(username=form.username.data,
                 email=form.email.data,
                 password=hashed_password)
        u.save()
        # db.session.add(u)
        # db.session.commit()
        flash(
            f'Account created for {form.username.data}! Please login', 'success')
        return redirect(url_for('users.login'))

    return render_template('register.html', title='Register', form=form)


@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash(f'Login Unsuccessful. Please check email and password', 'danger')

    return render_template('login.html', title='Login', form=form)


@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = AccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            filename = save_picture(form.picture.data)
            current_user.image_file = filename
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.save()
        flash('Your account has been updated', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for(
        'static', filename=f'profile_pics/{current_user.image_file}')
    return render_template('account.html',
                           title='Account',
                           image_file=image_file,
                           form=form)


@users.route('/user/<string:username>')
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
                .order_by(Post.date_posted.desc())\
                .paginate(per_page=5, page=page)
    return render_template('user_posts.html', posts=posts, user=user)


@users.route('/reset_password', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request_password.html', title='Reset Password', form=form)


@users.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_password_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user.password = hashed_password
        user.save()
        flash(
            f'Your password has been updated!', 'success')
        return redirect(url_for('users.login'))

    return render_template('reset_token.html', title='Reset Password', form=form)
