from flask import Flask, render_template, request, redirect, send_file, render_template_string
from static.scripts import db_actions as db
import json, shutil
from datetime import datetime as dt
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

roles = [
    'Сотрудник отдела по работе с клиентами',
    'Начальник отдела по работе с клиентами',
    'Сотрудник экономического отдела',
    'Начальник экономического отдела',
    'Директор',
    'Начальник производства',
    'Сотрудник производства',
    'Сотрудник отдела логистики',
    'Начальник отдела логистики'
]


def init_func():
    os.makedirs(os.path.join(app.instance_path), exist_ok=True)
    db.create()
    db.register('users', 'root', 'root', 'root', 'root')


@app.route("/login")
def login():
    return render_template('login.html')


@app.route("/registration")
def registration():
    uId = request.cookies.get('uId')
    user = db.get_table('users', email=str('None' if uId is None else uId))
    if user is not None and user['role'][0] == 'root':
        return render_template('registration.html')
    else:
        return render_template_string('<h1>No access</h1>')


@app.route("/admin")
def admin_panel():
    return render_template('admin.html')


@app.route("/")
def main_page():
    uId = request.cookies.get('uId')
    if not db.login('users', uId):
        return redirect('/login')
    # TABLES VISIBILITY
    table = db.get_table('tasks')
    acc_ids = []
    if table is not None:
        for x in range(len(table['id'])):
            acc = has_access(uId, table['id'][x])
            if acc == 'r' or acc == 'rw':
                acc_ids.append(table['id'][x])
        dicts = []
        for i in range(len(table['id'])):
            if table['id'][i] in acc_ids:
                dicts.append(db.get_table('tasks', id=table['id'][i]))

        t = {}
        for d in dicts:
            for k, v in d.items():  # d.items() in Python 3+
                t.setdefault(k, []).append(v)
    role = db.get_table('users', email=uId)['role'][0]
    # ADD BTN VISIBILITY
    if role == roles[0] or role == 'root':
        visibility = 'visible'
    else:
        visibility = 'hidden'

    if table is not None:
        return render_template('main.html', table=t, l=len(t['id']), visibility=visibility)
    else:
        return render_template('main.html', table=[[]], l=0)


# API
@app.route('/login_action', methods=['POST'])
def login_action():
    if request.headers['Web']:
        e = request.json['email']
        p = request.json['password']
        s = db.login('users', e, p)
        if s:
            return [{'status': 'success', 'uId': e}, 200, {'ContentType': 'application/json'}]
        else:
            return [{'status': 'failed'}, 200, {'ContentType': 'application/json'}]


@app.route('/registration_action', methods=['POST'])
def registration_action():
    if request.headers['Web']:
        n = request.json['name']
        e = request.json['email']
        p = request.json['password']
        r = request.json['role']
        s = db.register('users', e, n, p, r)

        if s:
            return json.dumps({'status': 'success', 'username': e}), 200, {'ContentType': 'application/json'}
        else:
            return json.dumps({'status': 'failed'}), 200, {'ContentType': 'application/json'}


@app.route('/new_request', methods=['POST'])
def new_task():
    if request.headers['Web']:
        n = request.json['name']
        p = request.json['phone']
        cc = request.json['country_code']
        e = request.json['email']
        d = request.json['desc']
        c = request.cookies.get('uId')
        db.create_new_task(n, p, cc, e, d, 'tasks', c)
        return json.dumps({'status': 'success', 'username': e}), 200, {'ContentType': 'application/json'}


@app.route('/open_task_editor', methods=['POST'])
def open_task_editor():
    if request.headers['Web']:
        uId = request.cookies.get('uId')
        id = request.json['table_id']
        data = db.get_table('tasks', id=id)
        data_docs = db.get_table('documentations', t_id=id)
        acc = has_access(uId, id)
        if data_docs is not None:
            return [{'status': 'success'},
                    [data['id'], data['status'], data['client_name'], data['client_phone'], data['client_email'],
                     data['short_description'], timectime(data['creation_date'][0]), data['creator'],
                     timectime(data['last_reassignment'][0]), data['current_worker'], data['description']],
                    [data['agreed_production'], data['agreed_economy']],
                    [data_docs['doc_name'], data_docs['doc_type'], data_docs['creator']],
                    {'access':acc}]
        else:
            return [{'status': 'success'},
                    [data['id'], data['status'], data['client_name'], data['client_phone'], data['client_email'],
                     data['short_description'], timectime(data['creation_date'][0]), data['creator'],
                     timectime(data['last_reassignment'][0]), data['current_worker'], data['description']],
                    [data['agreed_production'], data['agreed_economy']], []]
        # return [{'status': 'access_denied'}, data, 200, {'ContentType': 'application/json'}]


@app.route('/upload_docs', methods=['POST'])
def upload():
    dn = request.form['dn']
    dt_ = request.form['dt']
    t_id = request.form['t_id']
    f = request.files['file']
    c = request.cookies.get('uId')
    count = 0
    if not os.path.exists(os.path.join(app.instance_path, t_id)):
        os.makedirs(os.path.join(app.instance_path, t_id))
    if os.path.exists(os.path.join(app.instance_path, t_id, secure_filename(f.filename))):
        for path in os.listdir(os.path.join(app.instance_path, t_id)):
            if os.path.isfile(os.path.join(app.instance_path, t_id, path)):
                count += 1
        fname = str(count) + secure_filename(f.filename)
        f.save(os.path.join(app.instance_path, t_id, fname))
    else:
        fname = secure_filename(f.filename)
        f.save(os.path.join(app.instance_path, t_id, fname))
    db.upload_docs(dt_, dn, fname, t_id, c)
    return [{'status': 'success'}, 200]


@app.route('/open_doc_editor', methods=['POST'])
def open_doc_editor():
    id = request.json['id']
    t_id = request.json['task_id']
    s = db.get_table('documentations', id=id, t_id=t_id)
    return [{"status": "success"},
            {'doc_name': s['doc_name'], 'creator': s['creator'], 'doc_type': s['doc_type'], 'doc_path': s['doc_path']}]


@app.route('/download')
def download_file():
    t_id = request.args.get('task_id')
    f_n = request.args.get('f_name')
    return send_file(os.path.join(app.instance_path, t_id, f_n), as_attachment=True)


@app.route('/delete_doc', methods=['POST'])
def delete_doc():
    type = request.json['type']
    id = request.json['id']
    t_id = request.json['t_id']
    path = request.json['path']
    if type == 'doc':
        db.delete_row('documentations', id=id, t_id=t_id)
        os.remove(os.path.join(app.instance_path, path))
        return [{'status': 'success'}]
    if type == 'task':
        db.delete_row('tasks', id=t_id)
        try:
            db.delete_row('documentations', id='*', t_id=t_id)
            shutil.rmtree(os.path.join(app.instance_path, t_id))
        except:
            pass
        return [{'status': 'success'}]


@app.route('/update_doc', methods=['POST'])
def update_doc():
    id = request.form['id']
    try:
        f = request.files['file']
    except:
        pass
    d_n = request.form['dn']
    d_t = request.form['dt']
    t_id = request.form['t_id']
    count = 0
    if not os.path.exists(os.path.join(app.instance_path, t_id)):
        os.makedirs(os.path.join(app.instance_path, t_id))
    if os.path.exists(os.path.join(app.instance_path, t_id, secure_filename(f.filename))):
        for path in os.listdir(os.path.join(app.instance_path, t_id)):
            if os.path.isfile(os.path.join(app.instance_path, t_id, path)):
                count += 1
        fname = str(count) + secure_filename(f.filename)
        f.save(os.path.join(app.instance_path, t_id, fname))
    else:
        fname = secure_filename(f.filename)
        f.save(os.path.join(app.instance_path, t_id, fname))

    id = db.get_table('documentations', t_id=t_id)['id'][int(id) - 1]
    db.update_docs(id, d_t, d_n, fname)
    return [{'status': 'success'}]


@app.route('/publish', methods=['POST'])
def change_status():
    id = request.json['id']
    status = request.json['status']
    db.set_status(id, status)
    return [{'status': 'success'}]


@app.route('/save_task', methods=['POST'])
def save_task():
    id = request.json['id']
    client = request.json['client']
    phone = request.json['phone']
    email = request.json['email']
    short_desc = request.json['short_desc']
    desc = request.json['desc']
    prod = request.json['prod']
    econ = request.json['econ']
    db.update_task(id, client, phone, email, short_desc, desc, prod, econ)
    return [{'status': 'success'}]


def has_access(u_em, t_id):
    u_role = db.get_table('users', email=u_em)['role'][0]
    p_stat = db.get_table('tasks', id=t_id)['status'][0]
    if p_stat == 'Проект':
        if u_role == roles[0] or u_role == 'root':
            return 'rw'
        else:
            return 'forbidden'
    if p_stat == 'Размещена':
        if u_role == roles[0]:
            return 'r'
        if u_role == roles[1] or u_role == 'root':
            return 'rw'
        else:
            return 'forbidden'

    if p_stat == 'Изменение':
        if u_role == roles[0] or u_role == 'root':
            return 'rw'
        else:
            return 'forbidden'
    if p_stat == 'Принята на рассмотрение':
        if u_role in roles[0:5] or u_role == 'root':
            return 'r'
        else:
            return 'forbidden'


def merge_dict(dicts_list):
    d = {**dicts_list[0]}
    for entry in dicts_list[1:]:
        for k, v in entry.items():
            d[k] = ([d[k], v] if k in d and type(d[k]) != list
                    else [*d[k], v] if k in d
                    else v)
    return d


@app.route('/accept_task', methods=['POST'])
def accept():
    id = request.json['id']
    stat = request.json['status']
    db.set_status(id, stat)
    return [{'status': 'success'}]


@app.route('/reject', methods=['POST'])
def reject():
    id = request.json['id']
    stat = request.json['status']
    reason = request.json['reason']
    db.reject_task(id, stat, reason)
    return [{'status': 'success'}]


# JINJA FILTERS
@app.template_filter('ctime')
def timectime(s):
    return dt.fromtimestamp(s).replace(second=0, microsecond=0)
