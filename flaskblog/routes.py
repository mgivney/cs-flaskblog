from flask import url_for, flash, redirect
from flask.templating import render_template
from flaskblog.forms import RegistrationForm, LoginForm
from flaskblog import app

posts = [
    {
        'author': 'George Washington',
        'title': 'First Blog Post',
        'content' : '''Lorem ipsum dolor sit amet, consectetur adipisicing
                     elit. Consequuntur, dolor? Voluptatibus quia fugit 
                     culpa laboriosam repellendus soluta ipsam, aliquid est.''',
        'date_posted': '04-21-1775'
    },
    {
        'author': 'James Madison',
        'title': 'Second Blog Post',
        'content' : '''Lorem ipsum dolor sit amet, consectetur adipisicing
                     elit. Consequuntur, dolor? Voluptatibus quia fugit 
                     culpa laboriosam repellendus soluta ipsam, aliquid est.''',
        'date_posted': '04-21-1779'
    },
]

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', posts=posts)


@app.route('/about')
def about():
    return render_template('about.html', title='About Us')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))

    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data=='password':
            flash(f'You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash(f'Login Unsuccessful. Please check username or password', 'danger')

    return render_template('login.html', title='Login', form=form)
