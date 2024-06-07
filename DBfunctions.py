import sqlite3 as sl

class DB:
    def __init__(self):
        self.connection = sl.connect('My/delivery_service.db', check_same_thread=False)
        self.insert_dict = self.filling_insert_dict()
        self.select_dict = self.filling_select_dict()

    def create(self):
        with self.connection:
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS Users (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    tg_chat_id varchar(15),
                    name varchar(60),
                    tel integer unique,
                    email varchar(40) unique,
                    adress varchar(50),
                    is_admin integer null DEFAULT NULL
                    );
                """)
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS Orders (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    user_id integer,
                    is_delivered integer,
                    ordered_time datetime,
                    cooking_time datetime,
                    adress varchar(50)
                    );
                """)
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS Dishes (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    name varchar(40),
                    category varchar(40),
                    price real,
                    cooking_time datetime,
                    img varchar(250),
                    is_on_stop integer
                    );
                """)
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS DishesOrders (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    dishes_id integer,
                    orders_id integer,
                    count integer
                    );
                """)
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS Comments (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    dishes_id integer,
                    user_id integer,
                    text TEXT
                    );
                """)
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS Dishes_comment (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    user_id integer,
                    dishes_id integer,
                    stars integer
                    );
                """)

    def filling_tables(self):
        for key, value in self.insert_dict.items():
            if key == 'Users':
                self.insert(key, ['3fdf5g544', 'Николай', 293956447, 'jfhg@gmail.com', 'Г Минск Пр Держинского', None])
                self.insert(key, ['nfj4j3nj4', 'Евгения', 293954547, 'djkfj@gmail.com', 'Г Минск Пр Держинского', None])
                # self.insert(key, ['u8h3ruhr3', 'Софья', None, None, None, 1])
            elif key == 'Orders':
                self.insert(key, [1, 1, '20240519 15:40:00', '50', 'г Минск, пр Держинского 154'])
            elif key == 'DishesOrders':
                self.insert(key, [1, 1, 1])
                self.insert(key, [3, 1, 2])
            elif key == 'Dishes':
                self.insert(key, ['Пицца', 'Обед', 20, '40', 'IMG/pizza.jpg', 0])
                self.insert(key, ['Омлет', 'Завтрак', 17, '25', 'IMG/omelet.jpg', 0])
                self.insert(key, ['Фо-бо', 'Ужин', 33, '35', 'IMG/fobo.jpg', 0])
                self.insert(key, ['Роллы', 'Ужин', 45, '40', 'IMG/sushi.jpg', 1])
            elif key == 'Comments':
                self.insert(key, [1, 1, 'Блюдо превосходное'])
            elif key == 'Dishes_comment':
                self.insert(key, [1, 1, 5])

    def sql_insert_row(self, table_name):
        with self.connection:
            cur = self.connection.execute(f'Pragma table_info ("{table_name}")')
            col = cur.fetchall()

            col_num = len(col)
            sql_insert = f"INSERT OR IGNORE INTO {table_name}("
            for ind, i in enumerate(col):
                if i[1] == 'id':
                    continue
                sql_insert += i[1]
                if ind == col_num - 1:
                    sql_insert += ') '
                else:
                    sql_insert += ','
            sql_insert += 'values ('
            for i in range(col_num - 1):
                sql_insert += '?'
                if i == col_num - 2:
                    sql_insert += ') '
                else:
                    sql_insert += ','
            return sql_insert

    def filling_insert_dict(self):
        with self.connection:
            cur = self.connection.execute('SELECT name FROM sqlite_master WHERE type="table"')
            insert_dict = {}
            for i in cur:
                if i[0] == 'sqlite_sequence':
                    continue
                insert_dict[i[0]] = self.sql_insert_row(i[0])
            return insert_dict

    def insert(self, table_name, list_of_val, sql_insert=None):
        with self.connection:
            if sql_insert:
                self.connection.execute(sql_insert, list_of_val)
            else:
                self.connection.execute(self.insert_dict[table_name], list_of_val)

    def select_sql(self, table_name):
        with self.connection:
            cur = self.connection.execute(f'Pragma table_info ("{table_name}")')
            col = cur.fetchall()

            col_num = len(col)
            select_sql = 'SELECT '
            for ind, i in enumerate(col):
                if i[1] == 'adress' and table_name == 'Users':
                    col_num -= 1
                if table_name == 'Users' and i[1] == 'is_admin':
                    continue

                select_sql += i[1]
                if ind != col_num - 1:
                    select_sql += ','
            select_sql += f' FROM {table_name}'
            return select_sql

    def execute_select_sql(self, query, params=None):
        with self.connection:
            cur = self.connection.cursor()
            if params:
                cur.execute(query, params)
            else:
                cur.execute(query)
            result = cur.fetchall()
        return result

    def filling_select_dict(self):
        with self.connection:
            cur = self.connection.execute('SELECT name FROM sqlite_master WHERE type="table"')
            select_dict = {}
            for i in cur:
                if i[0] == 'sqlite_sequence':
                    continue
                select_dict[i[0]] = self.select_sql(i[0])
            return select_dict

    def select(self, table_name):
        with self.connection:
            cur = self.connection.execute(self.select_dict[table_name])
            data = cur.fetchall()
        return data

    def new_client(self, list_of_val):
        sql_insert = 'INSERT OR IGNORE INTO Users(tg_chat_id,name,tel,email,adress) values (?,?,?,?,?)'
        self.insert('Users', list_of_val, sql_insert)

    def categories(self):
        categories = []
        with self.connection:
            cur = self.connection.execute('SELECT category FROM Dishes')
            for i in cur:
                if i[0] not in categories:
                    categories.append(i[0])
        return categories

    def my_orders(self, tg_chat_id):
        sql_select = """SELECT * 
                        FROM Orders 
                        INNER JOIN Users ON Users.id = Orders.user_id
                        WHERE Users.tg_chat_id = ? and Orders.is_delivered=0;
                    """
        with self.connection:
            cur = self.connection.execute(sql_select, [tg_chat_id])
            data = cur.fetchall()
        return data

    def orders_history(self, tg_chat_id):
        sql_select = """SELECT Orders.* 
                                FROM Orders 
                                INNER JOIN Users ON Users.id = Orders.user_id
                                WHERE Users.tg_chat_id = ? and Orders.is_delivered=1;
                            """
        with self.connection:
            cur = self.connection.execute(sql_select, [tg_chat_id])
            data = cur.fetchall()
        return data

    def is_registered(self, tg_chat_id):
        with self.connection:
            sql = self.select_dict['Users'] + f' WHERE tg_chat_id="{tg_chat_id}"'
            cur = self.connection.execute(sql)
            data = cur.fetchall()
            if data:
                return True
            else:
                return False

    def get_client_data(self, tg_chat_id):
        with self.connection:
            sql_select = self.select_dict['Users'] + f' WHERE tg_chat_id="{tg_chat_id}"'
            cur = self.connection.execute(sql_select)
            data = cur.fetchall()
            return data[0]

    def menu_data_on_category(self, category):
        sql_str = f'SELECT id,name,category,price,cooking_time,img FROM Dishes WHERE category="{category}" AND is_on_stop=0'
        with self.connection:
            cur = self.connection.execute(sql_str)
            data = cur.fetchall()
        return data

    def on_stop(self, dish_id, flag):
        sql_update = f'UPDATE Dishes SET is_on_stop={flag} WHERE id={dish_id}'
        with self.connection:
            cur = self.connection.execute(sql_update)

    def max_cooking_time(self, dish_id_list):
        sql_ids = '('
        col_num = len(dish_id_list)
        for ind, id in enumerate(dish_id_list):
            sql_ids += str(id)
            if ind != col_num - 1:
                sql_ids += ', '
        sql_ids += ')'
        sql = 'SELECT cooking_time FROM Dishes WHERE id in '
        sql += sql_ids

        with self.connection:
            cur = self.connection.execute(sql)
            list_of_cooking_time = cur.fetchall()

        max_cooking_time = max(list_of_cooking_time)
        return max_cooking_time[0]

    def new_order(self, tg_chat_id, ordered_time, dish_data):
        # Orders
        sql_adress = f'SELECT adress FROM USERS WHERE tg_chat_id="{tg_chat_id}"'
        sql_user_id = f'SELECT id FROM USERS WHERE tg_chat_id="{tg_chat_id}"'

        dishes_id = []
        for dish in dish_data:
            dishes_id.append(dish[0])

        cooking_time = self.max_cooking_time(dishes_id)

        with self.connection:
            cur = self.connection.execute(sql_adress)
            adress = cur.fetchone()

            cur = self.connection.execute(sql_user_id)
            user_id = cur.fetchone()

        list_of_val = [user_id[0], 0, ordered_time, cooking_time, adress[0]]
        self.insert('Orders', list_of_val)

        # DishesOrders
        sql_order_id = 'SELECT id FROM Orders ORDER BY id DESC LIMIT 1'
        with self.connection:
            cur = self.connection.execute(sql_order_id)
            order_id = cur.fetchone()
            order_id = order_id[0]

            for dish_id, count in dish_data:
                list_of_val =  [dish_id, order_id, count]
                self.insert('DishesOrders', list_of_val)


    def dishes_data(self, order_id):
        sql = f'SELECT Dishes.id, Dishes.name, DishesOrders.count, Dishes.price FROM DishesOrders INNER JOIN Dishes ON Dishes.id = DishesOrders.dishes_id WHERE orders_id={order_id}'

        with self.connection:
            cur = self.connection.execute(sql)
            data = cur.fetchall()
        return data

    def order_is_delivered(self, order_id):
        sql = f'UPDATE Orders SET is_delivered=1 WHERE id = {order_id}'
        with self.connection:
            self.connection.execute(sql)

    def update_client_data(self, tg_chat_id, list_of_val):
        name = list_of_val[0]
        tel = list_of_val[1]
        email = list_of_val[2]
        adress = list_of_val[3]

        sql = f'UPDATE Users SET name="{name}", tel={tel}, email="{email}", adress="{adress}" WHERE tg_chat_id="{tg_chat_id}"'
        with self.connection:
            self.connection.execute(sql)

    def dish_data_on_name(self, name):
        sql = self.select_sql('Dishes') + f' WHERE name="{name}"'
        with self.connection:
            cur = self.connection.execute(sql)
            data = cur.fetchone()
        return data

    def dish_data_on_id(self, dish_id):
        sql = self.select_sql('Dishes') + f' WHERE id={dish_id}'
        with self.connection:
            cur = self.connection.execute(sql)
            data = cur.fetchone()
        return data

    def initialize_super_admin(self):
        SUPER_ADMIN_TG_CHAT_ID = '7039255546'
        SUPER_ADMIN_NAME = 'Mirik'
        with self.connection:
            sql = f'SELECT * FROM Users WHERE is_admin=1'
            cur = self.connection.execute(sql)
            data = cur.fetchall()
            if not data:
                sql_insert = 'INSERT OR IGNORE INTO Users(tg_chat_id,name,is_admin) values (?,?,?)'
                self.connection.execute(sql_insert, [SUPER_ADMIN_TG_CHAT_ID, SUPER_ADMIN_NAME,  1])

    def is_super_admin(self, user_id):
        with self.connection:
            sql = 'SELECT is_admin FROM Users WHERE tg_chat_id=?'
            result = self.connection.execute(sql, (user_id,)).fetchone()
        return result is not None and result[0] == 1

    def add_admin(self, list_of_val):
        insert_sql = 'INSERT OR IGNORE INTO Users(tg_chat_id,name,tel,email,adress,is_admin) values (?,?,?,?,?,0)'
        self.insert('Users', list_of_val, insert_sql)

    def get_admins(self):
        sql = 'SELECT tg_chat_id, name  FROM Users WHERE is_admin=0'
        with self.connection:
            cur = self.connection.execute(sql)
            data = cur.fetchall()
        return data

    def update_admin(self, tg_chat_id, name):
        sql = f'UPDATE Users SET name="{name}" WHERE tg_chat_id="{tg_chat_id}"'
        with self.connection:
            self.connection.execute(sql)

    def get_dishes(self):
        return self.select('Dishes')


db = DB()

if __name__ == '__main__':
    db.create()
    db.filling_tables()
    db.initialize_super_admin()
