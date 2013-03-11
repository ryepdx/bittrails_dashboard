import json
from flask import render_template, Blueprint, request
from flask.ext.login import current_user
from auth import API
app = Blueprint('terminal', __name__, template_folder='templates')

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == "POST":
        response = API.get(request.form.get('cmd'), user = current_user)
        status = response.status
        result = response.content
    else:
        result = None
        status = None
        
    return render_template('%s/index.html' % app.name,
        cmd = request.form.get('cmd', ''), status = status, result = result)
