from flask import Blueprint, render_template
from werkzeug.exceptions import NotFound, Unauthorized, InternalServerError

errors = Blueprint('errors', __name__)

@errors.app_errorhandler(NotFound)
def error_404(error):
  print('hit the 404 error')
  return render_template('errors/404.html', title='Not Found')


@errors.app_errorhandler(Unauthorized)
def error_403(error):
  return render_template('errors/403.html')


@errors.app_errorhandler(InternalServerError)
def error_500(error):
  return render_template('errors/500.html')
