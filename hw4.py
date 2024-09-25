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
    # Телефон не может дублироваться под разными id, но может быть привязан к
    # нескольким клиентам одновременно (в таблице clients_phones)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS phones(
        id SERIAL PRIMARY KEY,
        phone VARCHAR(30) UNIQUE
        );
        """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS clients_phones (
        client_id INTEGER NOT NULL REFERENCES clients(id),
        phone_id INTEGER NOT NULL REFERENCES phones(id),
        CONSTRAINT pk_clients_phone PRIMARY KEY (client_id, phone_id) 
        );
        """)

# 2. Функция, позволяющая добавить нового клиента.
def add_new_client(conn, id, name, surname, email):
    cur.execute("""
        INSERT INTO clients VALUES(%s, %s, %s, %s);
        """, (id, name, surname, email,))

# 3. Функция, позволяющая добавить телефон для существующего клиента.
def add_new_phone(conn, phone, id_client):
    # Проверяем, нет ли уже у клиента этого телефона.
    if id_client == find_client_id_by_phone(conn, phone):
        print(f"Номер телефона {phone} уже есть у этого клиента!")
    else:
        #Получаем id телефона и тем самым заодно проверяем его наличие в БД
        #(включая случаи, когда он почему-то не принадлежит ни одному клиенту)
        cur.execute ("""
        SELECT id FROM phones
        WHERE phone = %s;
            """,(phone,))
        id_phone_list = cur.fetchone()
        if id_phone_list == None:
        #Если такого номера телефона нет в БД:
            #Генерируем номер id для нового телефона (<самый большой id> + 1)
            cur.execute ("""
            SELECT MAX(id) FROM phones;
                """)
            max_id = cur.fetchone()
            if max_id[0] != None:
                id_phone = max_id[0] + 1
            else:
                #Если это вообще первый телефон в БД
                id_phone = 0
            #добавление нового телефона
            cur.execute("""
                INSERT INTO phones VALUES(%s, %s);
                """, (id_phone, phone,))
        else:
            id_phone = id_phone_list[0]
        #связь id телефона и id клиента
        cur.execute("""
            INSERT INTO clients_phones VALUES(%s, %s);
            """, (id_client, id_phone,))

# 4. Функция, позволяющая изменить данные о клиенте.
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
        sql_values = tuple(sql_values_list)
        cur.execute(sql_string, sql_values)

# 5. Функция, позволяющая удалить телефон для существующего клиента.
# У клиента может быть несколько телефонов, но удаляется лишь один из них.
# Если телефон принадлежит ещё кому-то, то удаляется лишь связь с конкретным лицом.
def delete_phone(conn, id_phone, id_client):
    #удаление связки id телефона и id клиента
    cur.execute("""
        DELETE FROM clients_phones 
        WHERE phone_id = %s AND client_id = %s;
        """, (id_phone, id_client,))
    conn.commit()
    #проверка, нет ли этого же телефона у других клиентов
    cur.execute("""
        SELECT client_id FROM clients_phones
        WHERE phone_id = %s
        """, (id_phone,))
    user_list = cur.fetchall()
    #Если нет других "хозяев" телефона, то он удаляется из БД
    if user_list == []:
        cur.execute("""
            DELETE FROM phones 
            WHERE id = %s;
            """, (id_phone,))

# 6. Функция, позволяющая удалить существующего клиента.
def delete_client(conn, id):
    #Поиск всех телефонов клиента
    cur.execute("""
        SELECT phone_id FROM clients_phones
        WHERE client_id = %s
    """, (id,))
    phones_id_list = cur.fetchall()
    #Если у клиента был хотя бы один телефон
    if phones_id_list != []:
        for phone_id in phones_id_list:
            #Удаление телефона
            delete_phone(conn, phone_id[0], id)
    #удаление клиента
    cur.execute("""
        DELETE FROM clients
        WHERE id = %s;
        """, (id,))

# 7. Функция, позволяющая найти клиента по его: имени, фамилии, email или телефону.
def search_client(conn, name = '', surname = '', email = '', phone = ''):
    result = []
    if (name == '') and (surname == '') and (email == '') and (phone == ''):
        #print ('Данных недостаточно...')
        pass
    else:
        #Список значений, которые подставятся в запрос
        sql_values_list = []
        #Формирование строки для запроса через psycopg2
        sql_string = """
            SELECT c.id, c.name, c.surname, c.email, p.id, p.phone FROM clients AS c
            LEFT JOIN clients_phones AS c_p ON c.id = c_p.client_id
            LEFT JOIN phones AS p ON c_p.phone_id = p.id
            WHERE """
        sql_string_append = []
        if name != '':
            sql_string_append.append("""c.name = %s""")
            sql_values_list.append(name)
        if surname != '':
            sql_string_append.append("""c.surname = %s""")
            sql_values_list.append(surname)
        if email != '':
            sql_string_append.append("""c.email = %s""")
            sql_values_list.append(email)
        if phone != '':
            sql_string_append.append("""p.phone = %s""")
            sql_values_list.append(phone)
        sql_string += f"""{' AND '.join(sql_string_append)};"""
        sql_values = tuple(sql_values_list)
        cur.execute(sql_string, sql_values)
        for fetch_tuple in cur.fetchall():
            result.append(fetch_tuple)
    return result

# Удаление таблиц из БД
def del_tables(conn):
    cur.execute("""
        DROP TABLE IF EXISTS clients CASCADE;
        DROP TABLE IF EXISTS phones CASCADE;
        DROP TABLE IF EXISTS clients_phones
        """)

# Функция для поиска id клиента/клиентов по номеру телефона:
# возвращает список с id (либо пустой список, если ничего не найдено)
def find_client_id_by_phone(conn, phone):
    result = []
    cur.execute ("""
    SELECT c_p.client_id FROM clients_phones AS c_p
    JOIN phones AS p ON c_p.phone_id = p.id 
    WHERE p.phone = %s;
        """, (phone,))    
    for fetch_tuple in cur.fetchall():
        result.append(fetch_tuple[0])
    return result

#Вывод всех таблиц БД:
def show_db(conn):
        print('----------')
        cur.execute("""
        SELECT * FROM clients;
        """)
        for f_tuple in cur.fetchall():
            print(f_tuple)
        print('-----')
        cur.execute("""
        SELECT * FROM phones;
        """)
        for f_tuple in cur.fetchall():
            print(f_tuple)
        print('-----')
        cur.execute("""
        SELECT * FROM clients_phones;
        """)
        for f_tuple in cur.fetchall():
            print(f_tuple)
        print('')


db, db_user, db_password = enter_db_user_credentials()

with psycopg2.connect(database = db, user = db_user, password = db_password) as conn:
    with conn.cursor() as cur:
        # 1. - Создание БД
        del_tables(conn)
        create_tables(conn)
        
        # 2.- Добавление новых клиентов
        add_new_client(conn, 0, 'Василий', 'Иванов', 'vasiliyivanov@qqq.q')
        add_new_client(conn, 1, 'Олег', 'Иванов', 'vasiliyivanov@qqq.q')
        add_new_client(conn, 2, 'Семён', 'Йцукенович', 'semyon@sss.s')
        add_new_client(conn, 3, 'Семён', 'Огогоев', 'ogogoev@ogogo.o')
        add_new_client(conn, 4, 'Иван', 'Огогоев', 'ivan@iii.i')
        add_new_client(conn, 5, 'Мария', 'Йцукеновна', 'mizukenovna@mmm.m')
        add_new_client(conn, 6, 'Василий', 'Иванов', 'mail@mmm.m')
        # У этих двух клиентов не будет телефона:
        add_new_client(conn, 7, 'Ольга', 'Беззвучная', 'olga@no-phone-club.cool')
        add_new_client(conn, 8, 'Игорь', 'Молчунов', 'igor@no-phone-club.cool')

        # 3. - Добавление телефона для существующих клиентов
        add_new_phone(conn, '+7 123 456 78 90', 0)
        add_new_phone(conn, '+7 234 567 89 01', 0)
        add_new_phone(conn, '+123 444 555 66 доб. 123', 2)
        add_new_phone(conn, '8-999-000-12-34', 3)
        #Такой же телефон у другого клиента (id 0):
        add_new_phone(conn, '+7 234 567 89 01',1)
        add_new_phone(conn, '12-34-56', 4)
        add_new_phone(conn, '7891011', 5)
        add_new_phone(conn, '8 123 456 01', 6)
        add_new_phone(conn, '8 123 456 02', 6)
        add_new_phone(conn, '8 123 456 03', 6)

        # 4. - Изменение данных о клиентах
        edit_client_data(conn, 1, 'ДЖЕЙН', 'ДОУ', '')
        edit_client_data(conn, 5, 'Мария', 'Фывапровна', 'marfiv@mmm.m')        
        
        # 5. - Удаление телефона для существующего клиента
        delete_phone(conn, 7, 6)
        #show_db(conn)

        #6. - Удаление существующего клиента
        delete_client(conn, 7)
        delete_client(conn, 6)
        delete_client(conn, 1)
        #show_db(conn)

        #7. - Поиск клиента по данным.
        print(search_client(conn))
        print(search_client(conn, surname = 'Иванов'))
        print(search_client(conn, email = 'marfiv@mmm.m'))
        print(search_client(conn, phone = '12-34-56'))
        print(search_client(conn, 'Мария', 'Фывапровна', 'marfiv@mmm.m', '7891011'))
        print(search_client(conn, name = 'Игорь', surname = 'Молчунов'))
conn.close()
