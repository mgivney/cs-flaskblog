import secrets
import os
from flask.helpers import url_for
from flask_mail import Message
from flaskblog import app, mail
from PIL import Image


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


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password visit the following link
{url_for('reset_password_token', token=token, _external=True)}    

If you did not make this request, simply ignore this email
'''
    mail.send(msg)
