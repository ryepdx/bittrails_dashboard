import json

from auth import API
from flask import render_template, Blueprint, request
from flask.ext.login import current_user
import urlparse

app = Blueprint('terminal', __name__, template_folder='templates')

@app.route('/', methods=['GET', 'POST'])
def home():
    http_method = request.form.get('method', "GET")
    
    if request.method == "POST":
        if http_method == "POST":
            url_parts = urlparse.urlsplit(request.form.get('cmd'))
            url = url_parts.path
            params = urlparse.parse_qs(url_parts.query)
            response = API.post(url, data = params, user = current_user)
        else:
            response = API.get(request.form.get('cmd'), user = current_user)
            
        status = response.status
        result = response.content if status == 200 else response.response.content
    else:
        result = None
        status = None
        
    return render_template('%s/index.html' % app.name,
        base_url = API.base_url, cmd = request.form.get('cmd', ''),
        result = json.dumps(result) if status == 200 else result,
        status = status, http_method = http_method)
