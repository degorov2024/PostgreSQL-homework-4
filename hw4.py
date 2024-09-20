import psycopg2

# Подключение к БД
def enter_db_user_credentials():
    print('Введите название базы данных:')
    db = str(input())
    print('Введите логин для доступа к БД:')
    user = str(input())
    print('Введите пароль:')
    password = str(input())   
    return db, user, password

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
    # Телефон может дублироваться под разными id...--------------------------------------------------------------------
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
        """, (id, name, surname, email))
    conn.commit()  # фиксируем в БД

# 3. Функция, позволяющая добавить телефон для существующего клиента.
def add_new_phone(conn, id_phone, phone, id_client):
    #добавление нового телефона
    cur.execute("""
        INSERT INTO phones VALUES(%s, %s);
        """, (id_phone, phone))
    #связь id телефона и id клиента
    cur.execute("""
        INSERT INTO clients_phones VALUES(%s, %s);
        """, (id_client, id_phone))
    conn.commit()

# 4. Функция, позволяющая изменить данные о клиенте. -------------------------------------------
def edit_client_data(conn, id, name='', surname='', email=''):
        #Список значений, которые подставятся в запрос
        sql_values_list = []
        #Формирование строки для запроса через psycopg2
        sql_string = """UPDATE clients SET """
        #Добавляем в SQL-запрос данные клиента, которые меняются
        if name != '':
            sql_string += """name = %s"""
            sql_values_list.append(name)
            if (surname != '') or (email != ''):
                sql_string += ', '
        if surname != '':
            sql_string += """surname = %s"""
            sql_values_list.append(surname)
            if email != '':
                sql_string += ', '
        if email != '':
            sql_string += """email = %s"""
            sql_values_list.append(email)
        sql_string += """ WHERE id=%s;"""
        sql_values_list.append(id)
        #В итоге получаем кортеж (если нужно поменять все данные клиента):
        #(name, surname, email, id)
        print(sql_string)
        sql_values = tuple(sql_values_list)       
        cur.execute(sql_string, sql_values)
        conn.commit()

# 5. Функция, позволяющая удалить телефон для существующего клиента.
# (т.е. у клиента может быть несколько телефонов, но удаляется лишь один из них)
def delete_phone(conn, id_phone, id_client):
    #удаление связки id телефона и id клиента
    cur.execute("""
        DELETE FROM clients_phones 
        WHERE phone_id = %s AND client_id = %s;
        """, (id_phone, id_client))
        # cur.execute("""
        # SELECT * FROM clients_phones;
        # """)
    #удаление телефона
    cur.execute("""
        DELETE FROM phones 
        WHERE id = %s;
        """, (id_phone,))
    conn.commit()
    #--------------------------возможно, стоило бы пересмотреть принцип хранения телефонов в БД, т.к. могут дублироваться, если у них разные id

# 6. Функция, позволяющая удалить существующего клиента.
def delete_client():
    pass

# 7. Функция, позволяющая найти клиента по его: имени, фамилии, email или телефону.
def search_client():
    pass





db, db_user, db_password = enter_db_user_credentials()

with psycopg2.connect(database = db, user = db_user, password = db_password) as conn:
    #print('Подключение к БД успешно')
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

        add_new_phone(conn, 0, '+7 123 456 78 90', 0)
        add_new_phone(conn, 1, '+7 234 567 89 01', 0)
        add_new_phone(conn, 2, '+123 444 555 66 доб. 123', 2)
        add_new_phone(conn, 3, '8-999-000-12-34', 3)
        add_new_phone(conn, 4, '+7 234 567 89 01',1)
        add_new_phone(conn, 5, '12-34-56', 4)
        add_new_phone(conn, 6, '7891011', 5)
        add_new_phone(conn, 7, '8 123 456 01', 6)
        add_new_phone(conn, 8, '8 123 456 02', 6)
        add_new_phone(conn, 9, '8 123 456 03', 6)
        #Телефон-дубликат
        #add_new_phone(conn, 1, '+7 234 567 89 01', 0)                                                                        

        edit_client_data(conn, 1, 'ДЖЕЙН', 'ДОУ', '' )
        #-------------------------------------------------------------
        
        delete_phone(conn, 7, 6)
        
        delete_client()
        
        search_client()

        cur.execute("""
        SELECT * FROM clients;
        """)
        for tuple in cur.fetchall():
            print(tuple)
        print('---------')
        cur.execute("""
        SELECT * FROM phones;
        """)
        for tuple in cur.fetchall():
            print(tuple)
        print('----------')
        cur.execute("""
        SELECT * FROM clients_phones;
        """)
        for tuple in cur.fetchall():
            print(tuple)
        
        # print('----------')
        # cur.execute("""
        # SELECT * FROM clients_phones
        # WHERE phone_id = 1000
        # """)
        # print(cur.fetchall())