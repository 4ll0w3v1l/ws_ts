from flask import Flask, render_template, request
from static.scripts import db_actions as db
import json
from datetime import datetime as dt

app = Flask(__name__)


@app.route("/login")
def login():
    return render_template('login.html')


@app.route("/registration")
def registration():
    return render_template('registration.html')


@app.route("/admin")
def admin_panel():
    return render_template('admin.html')


@app.route("/")
def main_page():
    table = db.get_tasks()
    return render_template('main.html', table=table, l=len(table['id']))


# API
@app.route('/login_action', methods=['POST'])
def login_action():
    if request.headers['Web']:
        e = request.json['email']
        p = request.json['password']
        s = db.login('users', e, p)
        if s:
            return json.dumps({'status': 'success', 'username': e}), 200, {'ContentType': 'application/json'}
        else:
            return json.dumps({'status': 'failed'}), 200, {'ContentType': 'application/json'}


@app.route('/registration_action', methods=['POST'])
def registration_action():
    if request.headers['Web']:
        n = request.json['name']
        e = request.json['email']
        p = request.json['password']
        s = db.register('users', e, n, p)

        if s:
            return json.dumps({'status': 'success', 'username': e}), 200, {'ContentType': 'application/json'}
        else:
            return json.dumps({'status': 'failed'}), 200, {'ContentType': 'application/json'}


@app.route('/new_request', methods=['POST'])
def new_request():
    if request.headers['Web']:
        n = request.json['name']
        p = request.json['phone']
        cc = request.json['country_code']
        e = request.json['email']
        d = request.json['desc']
        db.create_new_task(n, p, cc, e, d)
        return json.dumps({'status': 'success', 'username': e}), 200, {'ContentType': 'application/json'}


# JINJA FILTERS
@app.template_filter('ctime')
def timectime(s):
    return dt.fromtimestamp(s).replace(second=0, microsecond=0)