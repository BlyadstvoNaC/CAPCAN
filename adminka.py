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
def add_dish_command(message):
    if not is_admin_or_super_admin(message.from_user.id):
        bot.send_message(message.chat.id, 'Вы не Администратор.')
        return
    bot.send_message(message.chat.id, 'Введите название блюда:')
    bot.register_next_step_handler(message, get_dish_name)

def get_dish_name(message):
    dish_data[message.chat.id] = {}
    dish_data[message.chat.id]['name'] = message.text
    bot.send_message(message.chat.id, 'Введите категорию блюда:')
    bot.register_next_step_handler(message, get_dish_category)

def get_dish_category(message):
    dish_data[message.chat.id]['category'] = message.text
    bot.send_message(message.chat.id, 'Введите цену блюда:')
    bot.register_next_step_handler(message, get_dish_price)

def get_dish_price(message):
    try:
        dish_data[message.chat.id]['price'] = float(message.text)
        bot.send_message(message.chat.id, 'Введите время готовки блюда (в формате HH:MM:SS):')
        bot.register_next_step_handler(message, get_dish_cooking_time)
    except ValueError:
        bot.send_message(message.chat.id, 'Неправильный формат цены. Попробуйте снова:')
        bot.register_next_step_handler(message, get_dish_price)

def get_dish_cooking_time(message):
    dish_data[message.chat.id]['cooking_time'] = message.text
    bot.send_message(message.chat.id, 'Введите ссылку на изображение блюда:')
    bot.register_next_step_handler(message, get_dish_img)

def get_dish_img(message):
    dish_data[message.chat.id]['img'] = message.text
    dish_data[message.chat.id]['is_on_stop'] = 0

    try:
        db.execute_select_sql('INSERT INTO Dishes (name, category, price, cooking_time, img, is_on_stop) VALUES (?, ?, ?, ?, ?, ?)',
                       (dish_data[message.chat.id]['name'], dish_data[message.chat.id]['category'], dish_data[message.chat.id]['price'],
                        dish_data[message.chat.id]['cooking_time'], dish_data[message.chat.id]['img'], dish_data[message.chat.id]['is_on_stop']))
        bot.send_message(message.chat.id, 'Блюдо добавлено.')
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при добавлении блюда: {e}")
    finally:
        dish_data.pop(message.chat.id, None)

@bot.message_handler(commands=['get_dishes'])
def get_dishes_command(message):
    if not is_admin_or_super_admin(message.from_user.id):
        bot.send_message(message.chat.id, 'Вы не Администратор.')
        return
    get_dishes(message)


def get_dishes(message):
    try:
        dishes = db.execute_select_sql('SELECT name, category, price, cooking_time, img FROM Dishes')
        if dishes:
            response = "Список блюд:\n"
            for dish in dishes:
                dish_info = f"Название: {dish[0]}\nКатегория: {dish[1]}\nЦена: {dish[2]}\nВремя готовки: {dish[3]}\nИзображение: {dish[4]}\n\n"
                if len(response) + len(dish_info) > 4096:
                    bot.send_message(message.chat.id, response)
                    response = ""
                response += dish_info
            if response:
                bot.send_message(message.chat.id, response)
        else:
            bot.send_message(message.chat.id, "Нет доступных блюд.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при получении списка блюд: {e}")



def get_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Супер Админ')
    btn2 = types.KeyboardButton('Блюда')
    btn3 = types.KeyboardButton('Добавить блюдо')
    btn4 = types.KeyboardButton('Заказы')
    btn5 = types.KeyboardButton('Комментарии')
    btn6 = types.KeyboardButton('Помощь')
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.from_user.id, "👋 Привет! Я бот админ-панели ресторана U Mirika!", reply_markup=get_main_menu())
    if is_admin_or_super_admin(message.from_user.id):
        bot.send_message(message.chat.id, '❓ Задайте интересующий вопрос.', reply_markup=get_main_menu())


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == '👋 Поздороваться':
        bot.send_message(message.from_user.id, '❓ Задайте интересующий вопрос', reply_markup=get_main_menu())

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
            add_dish_command(message)
        else:
            bot.send_message(message.chat.id, 'Вы не Администратор.')

    elif message.text == 'Блюда':
        if is_admin_or_super_admin(message.from_user.id):
            get_dishes_command(message)
        else:
            bot.send_message(message.chat.id, 'Вы не Администратор.')

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