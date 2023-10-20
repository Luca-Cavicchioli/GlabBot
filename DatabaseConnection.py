import sqlite3


def create_table():
    conn = sqlite3.connect('eventi.sqlite')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            event_name TEXT,
            event_desc TEXT,
            event_date TEXT,
            event_photo_path TEXT
        )
    ''')

     # Crea la tabella degli utenti
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            full_name TEXT,
            registration_status INTEGER,
            publication_permission INTEGER
        )
    ''')

    # Crea la tabella delle competenze
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            skill_name TEXT
        )
    ''')

    # Crea la tabella degli enti
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS organizations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            org_name TEXT,
            org_contact TEXT,
            org_type TEXT
        )
    ''')

    # Crea la tabella delle richieste di registrazione degli enti
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registration_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            org_id INTEGER,
            org_name TEXT,
            org_contact TEXT,
            org_type TEXT,
            request_status INTEGER
        )
    ''')

    conn.commit()
    conn.close()