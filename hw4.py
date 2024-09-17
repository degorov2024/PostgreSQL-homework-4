import psycopg2

def enter_db_user_credentials():
    print('Введите название базы данных:')
    db = str(input())
    print('Введите логин для доступа к БД:')
    user = str(input())
    print('Введите пароль:')
    password = str(input())   
    return db, user, password

# class Client:
#     def _init_(self, id, name, surname, email)
#         self.id = id
#         self.name = name
#         self.surname = surname
#         self.email = email
#         self.phones_id = []

# def showmenu()
#     print('Введите номер команды.\n 1 - добавить нового клиента.\n2 - добавить телефон для существующего клиента.\n3 - изменить данные о клиенте.\n4 - удалить телефон для существующего клиента.\n5 - удалить существующего клиента.\n 6- найти клиента по его данным: имени, фамилии, email или телефону.')

# Удаление таблиц из БД (для простоты тестирования)
def del_tables(conn):
    cur.execute("""
    DROP TABLE IF EXISTS clients CASCADE;
    DROP TABLE IF EXISTS phones CASCADE;
    DROP TABLE IF EXISTS clients_phones
        """)
    conn.commit()


# 1. Функция, создающая структуру БД (таблицы).
def create_tables(conn):    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clients(
            id SERIAL PRIMARY KEY,
            name VARCHAR(40) NOT NULL,
            surname VARCHAR(40) NOT NULL,
            email VARCHAR(40) NOT NULL,
            UNIQUE (name, surname, email)
        );
        """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS phones(
        id SERIAL PRIMARY KEY,
        phone VARCHAR(30)
        );
        """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS clients_phones (
        client_id INTEGER NOT NULL REFERENCES clients(id),
        phone_id INTEGER NOT NULL REFERENCES phones(id),
        CONSTRAINT pk_clients_phone PRIMARY KEY (client_id, phone_id) 
        );
        """)
    conn.commit()

# 2. Функция, позволяющая добавить нового клиента.
def add_new_client(conn, id, name, surname, email):
        cur.execute("""
        INSERT INTO clients VALUES(%s, %s, %s, %s);
        """, (id, name, surname, email,))
        conn.commit()  # фиксируем в БД

# 3. Функция, позволяющая добавить телефон для существующего клиента.
def add_new_phone():
    pass

# 4. Функция, позволяющая изменить данные о клиенте.
def edit_client_data():
    pass

# 5. Функция, позволяющая удалить телефон для существующего клиента.
def delete_phone():
    pass

# 6. Функция, позволяющая удалить существующего клиента.
def delete_client():
    pass

# 7. Функция, позволяющая найти клиента по его: имени, фамилии, email или телефону.
def search_client():
    pass



# https://stackoverflow.com/questions/28606423/remove-non-numeric-characters-in-a-column-character-varying-postgresql-9-3-5
# select regexp_replace('пример строки - test1234test45abc', '[^0-9]+', '', 'g');


db, db_user, db_password = enter_db_user_credentials()

with psycopg2.connect(database = db, user = db_user, password = db_password) as conn:
    print('Подключение к БД успешно')

# while True:
#     input = show_menu()

    with conn.cursor() as cur:
        del_tables(conn)
        create_tables(conn)
        
        add_new_client(conn, 0, 'Василий', 'Иванов', 'vasiliyivanov@qqq.q')
        add_new_client(conn, 1, 'Олег', 'Иванов', 'vasiliyivanov@qqq.q')
        add_new_client(conn, 2, 'Семён', 'Йцукенович', 'semyon@sss.s')
        add_new_client(conn, 3, 'Семён', 'Огогоев', 'ogogoev@ogogo.o')
        add_new_client(conn, 4, 'Иван', 'Огогоев', 'ivan@iii.i')
        add_new_client(conn, 5, 'Мария', 'Йцукеновна', 'mizukenovna@mmm.m')
        add_new_client(conn, 6, 'Василий', 'Иванов', 'mail@mmm.m')
        # Клиент-дубликат
        #add_new_client(7, 'Мария', 'Йцукеновна', 'mizukenovna@mmm.m')

        add_new_phone()
        
        edit_client_data()
        
        delete_phone()
        
        delete_client()
        
        search_client()

        # извлечение данных (R из CRUD)
        cur.execute("""
        SELECT * FROM clients;
        """)

        for tuple in cur.fetchall():
            print(tuple)