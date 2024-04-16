import psycopg2
from config import host, user, password, db_name, port

connection_string = f"dbname='{db_name}' user='{user}' host='{host}' password='{password}' port='{port}'"

def create_db_connection():
    try:
        connection = psycopg2.connect(connection_string)
        print("DataBase is ready!")
        connection.autocommit = True
        return connection
    except psycopg2.Error as e:
        print(f"Ошибка при подключении к базе данных: {e}")
        return None

def get_random_task(theme):
    connection = psycopg2.connect(connection_string)
    cursor = connection.cursor()
    query = f"SELECT task FROM tasks_for_theme_{theme}py ORDER BY RANDOM();"
    cursor.execute(query)
    result = cursor.fetchone()
    if result:
        print(f"Произошел запрос на задачу по python {theme}-го уровня")
        return result[0]
    else:
        print("В таблице tasks нет заданий.")
    cursor.close()
    connection.close()

def get_random_pet_project(): #Рандомный пет-проект
    connection = psycopg2.connect(connection_string)
    cursor = connection.cursor()
    query = "SELECT project FROM pet_projects ORDER BY RANDOM();" #таблица пет-проектов
    cursor.execute(query)
    result = cursor.fetchone()
    if result:
        print("Произошел запрос на пет-проект")
        return result[0]
    else:
        print("В таблице pet_projects нет заданий.")
    cursor.close()
    connection.close()

def get_theory():
    connection = psycopg2.connect(connection_string)
    cursor = connection.cursor()
    query = "SELECT content FROM theory_py;"
    cursor.execute(query)
    result = cursor.fetchone()
    if result:
        print("Кто-то изучает теорию")
        return result[0]
    else:
        print("Что-то пошло не так при создании функции")
    cursor.close()
    connection.close()

def create_table(name, content): #Создание таблиц 
    connection = psycopg2.connect(connection_string)
    cursor = connection.cursor()
    create_table_query = f'''
    CREATE TABLE {name} (
        id SERIAL PRIMARY KEY,
        {content} VARCHAR(1600)
    );
    ''' #изменяемое поле
    cursor.execute(create_table_query)
    connection.commit()
    cursor.close()
    connection.close()

    print(f"Таблица {name} успешно создана.")

def create_table_users(): #Создание таблиц 
    connection = psycopg2.connect(connection_string)
    cursor = connection.cursor()
    create_table_query = f'''
    CREATE TABLE users (
        id BIGINT PRIMARY KEY,
        username TEXT NOT NULL,
        discriminator TEXT NOT NULL,
        points INTEGER DEFAULT 0
    );
    ''' #изменяемое поле
    cursor.execute(create_table_query)
    connection.commit()
    cursor.close()
    connection.close()

    print(f"Таблица users успешно создана.")

def user_exists_in_db(connection, user_id):
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        return cursor.fetchone() is not None
    except Exception as e:
        print(f"Ошибка при проверке наличия пользователя в базе данных: {e}")
        return False
    finally:
        cursor.close()

def update_user_points(connection, user_id):
    cursor = connection.cursor()
    try:
        cursor.execute("UPDATE users SET points = points + 5 WHERE id = %s", (user_id,))
        connection.commit()
        print(f"Баллы пользователя {user_id} обновлены.")
    except Exception as e:
        print(f"Ошибка при обновлении баллов пользователя: {e}")
    finally:
        cursor.close()