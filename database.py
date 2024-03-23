import sqlite3


def prepare_database():
    try:
        conn = sqlite3.connect('sqlite3.db')
        c = conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY,
                            user_id INTEGER UNIQUE,
                            genre TEXT,
                            character TEXT,
                            user_request TEXT,
                            processed_response TEXT
                       );''')

    except sqlite3.Error as e:
        print("Ошибка при работе с SQLite:", e)
        return None, None


prepare_database()


def is_value_in_table(users, column_name, value):
    conn = sqlite3.connect(users)
    c = conn.cursor()
    c.execute(f"SELECT * FROM users WHERE {column_name} = ?", (value,))
    result = c.fetchone()
    conn.close()
    return result is not None


# для выдачи информации о настройках
def get_settings(user_id):
    db_file = 'sqlite3.db'
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute('SELECT genre, character FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        if row:
            genre, character = row
            return genre, character
    except sqlite3.Error as e:
        print("Ошибка при работе с SQLite:", e)
    finally:
        conn.close()
    return None, None


def get_character(user_id):
    db_file = 'sqlite3.db'
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute('SELECT character FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        if result and result[0] is not None:
            character = result[0]
            if character == 'человек':
                system_content_difficulty = 'Обычный человек, не выделяющийся в мире.'
            elif character == 'авантюрист':
                system_content_difficulty = ('Искатель приключений, вечно идёт в опасные места')
            elif character == 'торговец':
                system_content_difficulty = ('Тороговец, странствует или есть место где продаёт что-то')
            elif character == 'учёный':
                system_content_difficulty = ('Учёный, изучает интересные вещи')
            else:
                system_content_difficulty = 'Отвечай коротко и ясно.'
            return character, system_content_difficulty
    except sqlite3.Error as e:
        print("Ошибка при работе с SQLite:", e)
    finally:
        conn.close()
    return None, None


def get_genre(user_id):
    db_file = 'sqlite3.db'
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute('SELECT genre FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        if result and result[0] is not None:
            genre = result[0]
            if genre == 'RPG':
                system_content_subject = ('Мир магии, где  ждут увлекательные приключения и встречи с различными'
                                          ' мистическими существами. Исследуйте удивительные земли, овладевайте'
                                          ' магическими навыками и сразитесь с таинственными врагами.')
            elif genre == 'MOD':
                system_content_subject = (' Действие происходит в современном мире,'
                                          ' где технологии нашего века, на дворе 2024 год, учебные заведения,'
                                          ' торговые центры и офисы создают основу для приключений.')
            elif genre == 'action':
                system_content_subject = ('мир динамичных сюжетов, где ждут'
                                          ' захватывающие сражения, напряженные погони и битвы, рискуя жизнью'
                                          ' в каждой ситуации.')
            else:
                system_content_subject = 'Отвечай коротко и ясно.'
            return genre, system_content_subject
    except sqlite3.Error as e:
        print("Ошибка при работе с SQLite:", e)
    finally:
        conn.close()
    return None, None


def get_user_request(user_id):
    db_file = 'sqlite3.db'
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute('SELECT user_request FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        if result and result[0] is not None:
            user_request = result[0]
            return user_request
    except sqlite3.Error as e:
        print("Ошибка при работе с SQLite:", e)
    finally:
        conn.close()


def get_processed_response(user_id):
    db_file = 'sqlite3.db'
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute('SELECT processed_response FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        if result and result[0] is not None:
            processed_response = result[0]
            if len(processed_response) > 200:
                processed_response = "..."
            return processed_response
    except sqlite3.Error as e:
        print("Ошибка при работе с SQLite:", e)
    finally:
        conn.close()