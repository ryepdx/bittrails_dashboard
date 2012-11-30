from flask import render_template, Blueprint

app = Blueprint('home', __name__, template_folder='templates')

@app.route('/')
def index():
    return render_template('%s/index.html' % app.name)
