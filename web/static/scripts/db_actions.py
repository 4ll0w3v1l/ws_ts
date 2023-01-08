import sqlite3, hashlib

db_path = 'static/data.db'


def create():
    con = sqlite3.connect(db_path)

    cur = con.cursor()
    cur.executescript(
        'CREATE TABLE users(email varchar(255) PRIMARY KEY, "name" text, password text, role text);'
        'CREATE TABLE tasks(id int PRIMARY KEY, creation_date timestamp, status text, last_reassignment timestamp, reject_reason text, agreed_production int, agreed_economy int, client_name text, client_phone text, client_email text, description text, short_description text, current_worker varchar(250), creator varchar(250), FOREIGN KEY ("current_worker") REFERENCES users(email), FOREIGN KEY ("creator") REFERENCES users(email));'
        'CREATE TABLE documentations(id int PRIMARY KEY, doc_type varchar(250), creator varchar(250), doc_name varchar(250), doc_path text, FOREIGN KEY (creator) REFERENCES users(email));'
        )


def login(t, e, p):
    con = sqlite3.connect(db_path)

    cur = con.cursor()
    status = cur.execute(f'SELECT COUNT(1) FROM {t} WHERE email = ? AND password = ?',
                         (e, hashlib.sha256(p.encode()).hexdigest())).fetchall()
    return status[0][0]


def register(t, e, n, p):
    con = sqlite3.connect(db_path)
    try:
        cur = con.cursor()
        cur.execute(f'INSERT INTO {t}(email, name, password) VALUES(?, ?, ?)', (e, n, hashlib.sha256(p.encode()).hexdigest()))
        con.commit()
        return 1
    except:
        return 0