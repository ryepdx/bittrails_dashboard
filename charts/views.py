from flask import render_template, Blueprint, url_for, redirect
from flask.ext.login import current_user
from auth import API, BLUEPRINT

app = Blueprint('charts', __name__, template_folder='/templates')

@app.route('/')
def index():
    return render_template('%s/index.html' % app.name)
