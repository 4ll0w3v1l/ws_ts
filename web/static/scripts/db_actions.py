from datetime import datetime as dt
import sqlite3, hashlib

db_path = 'static/data.db'


def create():
    con = sqlite3.connect(db_path)

    cur = con.cursor()
    cur.executescript(
        'CREATE TABLE users(email varchar(255) PRIMARY KEY, "name" text, password text, role text);'
        'CREATE TABLE tasks(id int PRIMARY KEY, creation_date timestamp, status text, last_reassignment timestamp, agreed_production int, agreed_economy int, client_name text, client_phone text, client_email text, description text, short_description text, current_worker varchar(250), creator varchar(250), FOREIGN KEY ("current_worker") REFERENCES users(email), FOREIGN KEY ("creator") REFERENCES users(email));'
        'CREATE TABLE documentations(id int PRIMARY KEY, doc_type varchar(250), creator varchar(250), doc_name varchar(250), doc_path text, FOREIGN KEY (creator) REFERENCES users(email));'
    )
    con.close()


def login(t, e, p):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    status = cur.execute(f'SELECT COUNT(1) FROM {t} WHERE email = ? AND password = ?',
                         (e, hashlib.sha256(p.encode()).hexdigest())).fetchall()
    con.close()
    return status[0][0]


def register(t, e, n, p):
    con = sqlite3.connect(db_path)
    try:
        cur = con.cursor()
        cur.execute(f'INSERT INTO {t}(email, name, password) VALUES(?, ?, ?)',
                    (e, n, hashlib.sha256(p.encode()).hexdigest()))
        con.commit()
        con.close()
        return 1
    except:
        con.close()
        return 0


def get_tasks():
    out = {}
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    table = cur.execute(f'SELECT * FROM tasks').fetchall()
    con.close()
    keys = table[0].keys()
    for i in range(len(table)):
        for x in range(len(keys)):
            try:
                out[keys[x]].append(table[i][keys[x]])
            except:
                out[keys[x]] = [table[i][keys[x]]]
    return out


def create_new_task(n, p, cc, e, d, c=None):
    # NEED TO ADD CREATOR
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute(
        f'INSERT INTO tasks(id, creation_date, status, client_name, client_phone, client_email, short_description) VALUES(?, ?, ?, ?, ?, ?, ?)',
        (len(get_tasks()['id']) + 1, dt.timestamp(dt.now()), "Проект", n, str(cc) + str(p), e, d))
    con.commit()
    con.close()

