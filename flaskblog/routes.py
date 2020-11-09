from os import abort
from flask import url_for, flash, redirect, request
from flask.templating import render_template
from flask_login.utils import login_required, logout_user
from flaskblog.forms import PostForm, RegistrationForm, LoginForm, AccountForm
from flaskblog import app, db, bcrypt
from .models import Post, User
from flask_login import login_user, current_user
import secrets
import os
from PIL import Image


@app.route('/')
@app.route('/home')
def home():
    posts = Post.query.all()
    return render_template('home.html', posts=posts)


@app.route('/about')
def about():
    return render_template('about.html', title='About Us')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
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
        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash(f'Login Unsuccessful. Please check email and password', 'danger')

    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    # when we dont care about one of the values
    # you can represent it as an underscore
    _, fext = os.path.splitext(form_picture.filename)
    pic_filename = f'{random_hex}{fext}'
    picture_path = os.path.join(
        app.root_path, 'static/profile_pics', pic_filename)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return pic_filename


@app.route('/account', methods=['GET', 'POST'])
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
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for(
        'static', filename=f'profile_pics/{current_user.image_file}')
    return render_template('account.html',
                           title='Account',
                           image_file=image_file,
                           form=form)


@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        flash('Post is created!', 'success')
        post = Post(title=form.title.data,
                    content=form.content.data,
                    author=current_user)
        post.save()
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post', form=form, legend='New Post')


@app.route('/post/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.save()
        flash('Post has been updated', 'success')
        return redirect(url_for('get_post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')


@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))
