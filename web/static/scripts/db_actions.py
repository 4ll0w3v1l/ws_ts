from datetime import datetime as dt
import sqlite3, hashlib

db_path = 'static/data.db'


def create():
    con = sqlite3.connect(db_path)

    cur = con.cursor()
    cur.executescript(
        'CREATE TABLE users(email varchar(255) PRIMARY KEY, "name" text, password text, role text);'
        'CREATE TABLE tasks(id int PRIMARY KEY, creation_date timestamp, status text, last_reassignment timestamp, description text, agreed_production int, agreed_economy int, client_name text, client_phone text, client_email text, short_description text, current_worker varchar(250), creator varchar(250), FOREIGN KEY ("current_worker") REFERENCES users(email), FOREIGN KEY ("creator") REFERENCES users(email));'
        'CREATE TABLE documentations(id varchar(255) PRIMARY KEY, doc_type text, doc_name text, creator varchar(250), doc_path text, id_task varchar(250), FOREIGN KEY (creator) REFERENCES users(email), FOREIGN KEY (id_task) REFERENCES tasks(id));'
    )
    con.close()


def login(t, e, p=None):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    if p is not None:
        status = cur.execute(f'SELECT COUNT(1) FROM {t} WHERE email = ? AND password = ?',
                             (e, hashlib.sha256(p.encode()).hexdigest())).fetchall()
    else:
        status = cur.execute(f'SELECT COUNT(1) FROM {t} WHERE email = ?', (e,)).fetchall()
    con.close()
    return status[0][0]


def register(t, e, n, p, r):
    con = sqlite3.connect(db_path)
    try:
        cur = con.cursor()
        cur.execute(f'INSERT INTO {t}(email, name, password, role) VALUES(?, ?, ?, ?)',
                    (e, n, hashlib.sha256(p.encode()).hexdigest(), r))
        con.commit()
        con.close()
        return 1
    except:
        con.close()
        return 0


def get_table(t, email=None, id=None, t_id=None):
    out = {}
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    if t_id is not None and id is None:
        table = cur.execute(f'SELECT * FROM {t} WHERE id_task = ?', (t_id,)).fetchall()
    elif t_id is not None and id is not None:
        tmp = cur.execute(f'SELECT * FROM {t} WHERE id_task = ? GROUP BY id', (t_id,)).fetchall()
        table = cur.execute(f'SELECT * FROM {t} WHERE id = ?', (tmp[int(id) - 1][0],)).fetchall()
    elif email is not None:
        if email == '' or email == 'None':
            return None
        table = cur.execute(f'SELECT * FROM {t} WHERE email = ?', (email,)).fetchall()
    elif id is None and t_id is None:
        table = cur.execute(f'SELECT * FROM {t}').fetchall()
    else:
        table = cur.execute(f'SELECT * FROM {t} WHERE id = ?', (id,)).fetchall()
    con.close()
    try:
        keys = table[0].keys()
        for i in range(len(table)):
            for x in range(len(keys)):
                try:
                    out[keys[x]].append(table[i][keys[x]])
                except:
                    out[keys[x]] = [table[i][keys[x]]]
        return out
    except:
        return None


def create_new_task(n, p, cc, e, d, t, c):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    t_now = dt.timestamp(dt.now())
    try:
        cur.execute(
            f'INSERT INTO tasks(id, creation_date, status, client_name, client_phone, client_email, short_description, agreed_production, agreed_economy, creator, last_reassignment) VALUES(?, ?, ?, ?, ?, ?, ?, 0, 0, ?, ?)',
            (get_table(t)['id'][-1] + 1, t_now, "Проект", n, str(cc) + str(p), e, d, c, t_now))
    except:
        cur.execute(
            f'INSERT INTO tasks(id, creation_date, status, client_name, client_phone, client_email, short_description, agreed_production, agreed_economy, creator, last_reassignment) VALUES(?, ?, ?, ?, ?, ?, ?, 0, 0, ?, ?)',
            (1, t_now, "Проект", n, str(cc) + str(p), e, d, c, t_now))
    con.commit()
    con.close()


def upload_docs(dt_, dn, path, t_id, c=None):
    tmp = get_table('documentations')
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    if tmp is None:
        cur.execute(
            'INSERT INTO documentations(id, doc_type, doc_name, creator, doc_path, id_task) VALUES(1, ?, ?, ?, ?, ?)',
            (dt_, dn, c, path, t_id)
        )
    else:
        cur.execute(
            'INSERT INTO documentations(id, doc_type, doc_name, creator, doc_path, id_task) VALUES(?, ?, ?, ?, ?, ?)',
            (int(tmp['id'][-1]) + 1, dt_, dn, c, path, t_id)
        )
    con.commit()
    con.close()


def update_docs(id, d_t, d_n, d_p):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute(
        f'UPDATE documentations SET doc_type = ?, doc_name = ?, doc_path = ? WHERE id = ?', (d_t, d_n, d_p, id)
    )
    con.commit()
    con.close()
    return 1


def update_task(id, client, phone, email, short_desc, desc, prod, econ):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    if prod:
        prod = 1
    else:
        prod = 0
    if econ:
        econ = 1
    else:
        econ = 0

    cur.execute(
        f'UPDATE tasks SET description = ?, agreed_production = ?, agreed_economy = ?, client_name = ?, client_phone = ?, client_email = ?, short_description = ?, last_reassignment = {dt.timestamp(dt.now())}  WHERE id = ?',
        (desc, prod, econ, client, phone, email, short_desc, id))
    con.commit()
    con.close()
    return 1


def set_status(id, status):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute(f'UPDATE tasks SET status = ?, last_reassignment = {dt.timestamp(dt.now())} WHERE id = ?', (status, id))
    con.commit()
    con.close()


def reject_task(id, status, reason):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute(f'UPDATE tasks SET status = ?, description = ?, last_reassignment = {dt.timestamp(dt.now())} WHERE id = ?', (status, reason, id))
    con.commit()
    con.close()


def delete_row(t, id=None, t_id=None):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    if t_id is not None:
        if id == '*':
            cur.execute(f'DELETE FROM {t} WHERE id_task = ?', (t_id,))
        else:
            tmp = cur.execute(f'SELECT * FROM {t} WHERE id_task = ?', (t_id,)).fetchall()
            cur.execute(f'DELETE FROM {t} WHERE id = ?', (tmp[int(id) - 1][0],))
    if t_id is None:
        cur.execute(f'DELETE FROM {t} WHERE id = ?', id)
    con.commit()
    con.close()
