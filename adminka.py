import telebot
from telebot import types
#from My.Bot_Token import token
from DBfunctions import DB
import requests

bot = telebot.TeleBot('7073410632:AAGKQTCNrJvlJxZIHJHlr6k08TEt5sDRW0c')
db = DB()
#SUPER_ADMIN_CHAT_ID = "7039255546"

admins = {}

dish_data = {}

def is_admin(user_id):
    result = db.execute_select_sql('SELECT is_admin FROM Users WHERE tg_chat_id=?', (user_id,))
    if result:
        is_admin = result[0][0]
        return is_admin is not None and is_admin == 0
    return False

def is_super_admin(user_id):
    result = db.execute_select_sql('SELECT is_admin FROM Users WHERE tg_chat_id=?', (user_id,))
    if result:
        is_admin = result[0][0]
        return is_admin is not None and is_admin == 1
    return False

def is_admin_or_super_admin(user_id):
    return is_admin(user_id) or is_super_admin(user_id)


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("👋 Поздороваться")
    markup.add(btn1)
    bot.send_message(message.from_user.id, "👋 Привет! Я бот админ-панели ресторана U Mirika!", reply_markup=markup)


@bot.message_handler(commands=['add_admin'])
def add_admin(message):
    if not is_super_admin(message.from_user.id):
        bot.send_message(message.chat.id, 'Вы не Супер Админ.')
        return
    try:
        _, tg_chat_id, name, tel, email, adress = message.text.split()
        db.insert('Users', [tg_chat_id, name, tel, email, adress, 0])
        bot.send_message(message.chat.id, f"Администратор {name} добавлен.")
    except ValueError:
        bot.send_message(message.chat.id, "Неправильный формат. Используйте: /add_admin tg_chat_id name tel email adress")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")

@bot.message_handler(commands=['change_admin'])
def change_admin(message):
    if not is_super_admin(message.from_user.id):
        bot.send_message(message.chat.id, 'Вы не Супер Админ.')
        return
    try:
        _, tg_chat_id, new_name = message.text.split()
        if db.is_registered(tg_chat_id):
            old_name = db.get_client_data(tg_chat_id)[1]
            db.update('Users', 'name', new_name, tg_chat_id)
            bot.send_message(message.chat.id, f"Администратор {old_name} изменен на {new_name}.")
        else:
            bot.send_message(message.chat.id, "Администратор с таким ID не найден.")
    except ValueError:
        bot.send_message(message.chat.id, "Неправильный формат. Используйте: /change_admin tg_chat_id new_name")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")


@bot.message_handler(commands=['get_user_id'])
def get_user_id(message):
    try:
        _, username = message.text.split()
        chat_id = message.chat.id
        user = db.get_user_id_by_name(username)
        if user:
            user_id = user[0]
            bot.send_message(chat_id, f"User ID for {username} is {user_id}")
        else:
            bot.send_message(chat_id, f"User {username} not found")
    except ValueError:
        bot.send_message(message.chat.id, "Неправильный формат. Используйте: /get_user_id username")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")

def get_admins(chat_id):
    admins = db.get_admins()
    if admins:
        admin_list = [f"{admin[0]}: {admin[1]}" for admin in admins]
        admin_message = "Администраторы бота:\n" + "\n".join(admin_list)
    else:
        admin_message = "Список администраторов пуст."
    bot.send_message(chat_id, admin_message)



@bot.message_handler(commands=['add_dish'])
def add_dish(message):
    if not is_admin_or_super_admin(message.from_user.id):
        bot.send_message(message.chat.id, 'Вы не Администратор.')
        return
    dish_data[message.chat.id] = {}
    bot.send_message(message.chat.id, 'Введите название блюда:')
    bot.register_next_step_handler(message, get_dish_name)

# def get_dishes(chat_id):
#     if not is_admin_or_super_admin(chat_id):
#         bot.send_message(chat_id, 'Вы не Администратор.')
#         return
#     dishes = db.select('Dishes')
#     if dishes:
#         dish_list = "\n".join([f"{dish[1]} - {dish[2]}" for dish in dishes])
#         bot.send_message(chat_id, f"Список блюд:\n{dish_list}")
#     else:
#         bot.send_message(chat_id, "Список блюд пуст.")

@bot.message_handler(commands=['get_dishes'])
def get_dishes_command(message):
    get_dishes(message)

def get_dish_category(message):
    if not is_admin_or_super_admin(message.from_user.id):
        bot.send_message(message.chat.id, 'Вы не Администратор.')
        return
    dish_data[message.chat.id]['category'] = message.text
    bot.send_message(message.chat.id, 'Введите цену блюда:')
    bot.register_next_step_handler(message, get_dish_price)

def get_dish_price(message):
    if not is_admin_or_super_admin(message.from_user.id):
        bot.send_message(message.chat.id, 'Вы не Администратор.')
        return
    try:
        dish_data[message.chat.id]['price'] = float(message.text)
        bot.send_message(message.chat.id, 'Введите время готовки блюда (в формате HH:MM:SS):')
        bot.register_next_step_handler(message, get_dish_cooking_time)
    except ValueError:
        bot.send_message(message.chat.id, 'Неправильный формат цены. Попробуйте снова:')
        bot.register_next_step_handler(message, get_dish_price)

def get_dish_cooking_time(message):
    if not is_admin_or_super_admin(message.from_user.id):
        bot.send_message(message.chat.id, 'Вы не Администратор.')
        return
    try:
        dish_data[message.chat.id]['cooking_time'] = message.text
        bot.send_message(message.chat.id, 'Введите ссылку на изображение блюда:')
        bot.register_next_step_handler(message, get_dish_img)
    except ValueError:
        bot.send_message(message.chat.id, 'Неправильный формат времени готовки. Попробуйте снова:')
        bot.register_next_step_handler(message, get_dish_cooking_time)

def get_dish_img(message):
    if not is_admin_or_super_admin(message.from_user.id):
        bot.send_message(message.chat.id, 'Вы не Администратор.')
        return
    dish_data[message.chat.id]['img'] = message.text
    dish_data[message.chat.id]['is_on_stop'] = 0

    db.execute_select_sql('INSERT INTO Dishes (name, category, price, cooking_time, img, is_on_stop) VALUES (?, ?, ?, ?, ?, ?)',
                          (dish_data[message.chat.id]['name'], dish_data[message.chat.id]['category'],
                           dish_data[message.chat.id]['price'], dish_data[message.chat.id]['cooking_time'],
                           dish_data[message.chat.id]['img'], dish_data[message.chat.id]['is_on_stop']))
    bot.send_message(message.chat.id, f"Блюдо '{dish_data[message.chat.id]['name']}' добавлено.")
    dish_data.pop(message.chat.id)


def get_dishes(message):
    if not is_admin_or_super_admin(message.from_user.id):
        bot.send_message(message.chat.id, 'Вы не Администратор.')
        return

    categories = db.categories()

    if categories:
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        for category in categories:
            markup.add(types.KeyboardButton(category))

        bot.send_message(message.chat.id, "Выберите категорию блюд:", reply_markup=markup)
        bot.register_next_step_handler(message, handle_category_selection)
    else:
        bot.send_message(message.chat.id, "Список категорий пуст.")

@bot.message_handler(func=lambda message: True)
def handle_category_selection(message):
    categories = db.categories()
    if message.text in db.categories():
        category = message.text
        get_dishes_by_category(message, category)
    else:
        bot.send_message(message.chat.id, "Пожалуйста, выберите категорию из списка.")
    get_categories(message)

def get_dish_name(message):
    if not is_admin_or_super_admin(message.from_user.id):
        bot.send_message(message.chat.id, 'Вы не Администратор.')
        return
    dish_name = message.text
    dish_data[message.chat.id]['name'] = dish_name
    bot.send_message(message.chat.id, f'Вы добавляете блюдо с названием: {dish_name}. Теперь введите категорию блюда:')
    bot.register_next_step_handler(message, get_dish_category)


def get_dishes_by_category(message, category):
    if not is_admin_or_super_admin(message.from_user.id):
        bot.send_message(message.chat.id, 'Вы не Администратор.')
        return

    dishes = db.menu_data_on_category(category)
    if dishes:
        for dish in dishes:
            dish_name = dish[1]
            dish_category = dish[2]
            dish_price = dish[3]
            dish_cooking_time = dish[4]

            dish_info = f"Название: {dish_name}\nКатегория: {dish_category}\nЦена: {dish_price}\nВремя готовки: {dish_cooking_time}"
            bot.send_message(message.chat.id, dish_info)
    else:
        bot.send_message(message.chat.id, f"Список блюд в категории '{category}' пуст.")


def get_categories(message):
    if not is_admin_or_super_admin(message.from_user.id):
        bot.send_message(message.chat.id, 'Вы не Администратор.')
        return

    categories = db.categories()
    if categories:
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        for category in categories:
            markup.add(types.KeyboardButton(category))

        bot.send_message(message.chat.id, "Выберите категорию блюд:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Список категорий пуст.")

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    categories = db.categories()
    if message.text == '👋 Поздороваться':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('Супер Админ')
        btn2 = types.KeyboardButton('Блюда')
        btn3 = types.KeyboardButton('Добавить блюдо')
        btn4 = types.KeyboardButton('Заказы')
        btn5 = types.KeyboardButton('Комментарии')
        btn6 = types.KeyboardButton('Помощь')

        markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
        bot.send_message(message.from_user.id, '❓ Задайте интересующий вопрос', reply_markup=markup)  # ответ бота

    elif message.text == 'Супер Админ':
        if is_super_admin(message.from_user.id):
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn7 = types.KeyboardButton('Добавить администратора')
            btn8 = types.KeyboardButton('Изменить администратора')
            markup.add(btn7, btn8)
            bot.send_message(message.from_user.id, 'Привет, Супер Админ, выбери что хочешь сделать',
                             reply_markup=markup)
            get_admins(message.chat.id)
        else:
            bot.send_message(message.chat.id, 'Вы не Супер Админ.')

    elif message.text == 'Добавить администратора':
        if is_super_admin(message.from_user.id):
            bot.send_message(message.chat.id,
                             'Используйте команду /add_admin tg_chat_id name tel email adress для добавления администратора.')
        else:
            bot.send_message(message.chat.id, 'Вы не Супер Админ.')

    elif message.text == 'Изменить администратора':
        if is_super_admin(message.from_user.id):
            bot.send_message(message.chat.id,
                             'Используйте команду /change_admin user_id new_username для изменения администратора.')
        else:
            bot.send_message(message.chat.id, 'Вы не Супер Админ.')

    elif message.text == 'Добавить блюдо':
        if is_admin_or_super_admin(message.from_user.id):
            add_dish(message)
        else:
            bot.send_message(message.chat.id, 'Вы не Администратор.')

    elif message.text == 'Блюда':
        if is_admin_or_super_admin(message.from_user.id):
            get_categories(message)
        else:
            bot.send_message(message.chat.id, 'Вы не Администратор.')

    elif message.text == 'Выбрать категорию':

        get_dishes(message)

    elif message.text in categories:

        dishes_data = db.menu_data_on_category(message.text)

        if dishes_data:

             for dish in dishes_data:
                dish_info = f"Название: {dish[1]}\nКатегория: {dish[2]}\nЦена: {dish[3]}\nВремя готовки: {dish[4]}"

                bot.send_message(message.chat.id, dish_info)

        else:

            bot.send_message(message.chat.id, f"Список блюд в категории '{message.text}' пуст.")

    else:
        pass


# def dish_category(message):
#     category = message.text
#     if category in ['Салаты', 'Первые блюда', 'Горячие основные блюда', 'Закуски']:
#         bot.send_message(message.chat.id, f"Вы выбрали категорию: {category}. Введите название блюда: ")
#         bot.register_next_step_handler(message, save_dish)
#     else:
#         bot.send_message('Вы выбрали неверную категорию. Попробуйте снова')

        # markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        # bot.send_message(message.from_user.id, )



if __name__ == "__main__":
    print('Админ панель запущена')
    bot.infinity_polling(none_stop=True)