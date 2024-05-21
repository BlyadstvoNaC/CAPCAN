import sqlite3 as sl


class DB:
    def __init__(self):
        self.connection = sl.connect('My/delivery_service.db')
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
                self.insert(key, ['u8h3ruhr3', 'Софья', None, None, None, 1])
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
                if i[1] == 'id':
                    continue

                if i[1] == 'adress' and table_name == 'Users':
                    col_num -= 1
                if table_name == 'Users' and i[1] == 'is_admin':
                    continue

                select_sql += i[1]
                if ind != col_num - 1:
                    select_sql += ','
            select_sql += f' FROM {table_name}'
            return select_sql

    def select(self, table_name):
        with self.connection:
            cur = self.connection.execute(self.select_dict[table_name])
            data = cur.fetchall()
        return data

    def filling_select_dict(self):
        with self.connection:
            cur = self.connection.execute('SELECT name FROM sqlite_master WHERE type="table"')
            select_dict = {}
            for i in cur:
                if i[0] == 'sqlite_sequence':
                    continue
                select_dict[i[0]] = self.select_sql(i[0])
            return select_dict

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

    def new_order(self, order_data, dish_data):
        pass

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

    # def menu_on_category(self, category):
    #     sql_str = f'SELECT name FROM Dishes WHERE category="{category}" AND is_on_stop=0'
    #     cur = self.connection.execute(sql_str)
    #     data = cur.fetchall()
    #     lst_of_dishes = []
    #     for i in data:
    #         lst_of_dishes.append(i[0])
    #     return lst_of_dishes

    def on_stop(self, dish_id, flag):
        sql_update = f'UPDATE Dishes SET is_on_stop={flag} WHERE id={dish_id}'
        with self.connection:
            cur = self.connection.execute(sql_update)


db = DB()
db.create()
db.filling_tables()
