import telebot
from telebot import types

bot = telebot.TeleBot('7073410632:AAGKQTCNrJvlJxZIHJHlr6k08TEt5sDRW0c')

admins = {}


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("👋 Поздороваться")
    markup.add(btn1)
    bot.send_message(message.from_user.id, "👋 Привет! Я бот админ-панели ресторана U Mirika!", reply_markup=markup)


@bot.message_handler(commands=['add_admin'])
def add_admin(message):
    try:
        # Команда должна быть в формате /add_admin user_id username
        _, user_id, username = message.text.split()
        admins[int(user_id)] = username
        bot.send_message(message.chat.id, f"Администратор {username} добавлен.")
    except ValueError:
        bot.send_message(message.chat.id, "Неправильный формат. Используйте: /add_admin user_id username")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")

@bot.message_handler(commands=['change_admin'])
def change_admin(message):
    try:
        # Команда должна быть в формате /change_admin user_id new_username
        _, user_id, new_username = message.text.split()
        user_id = int(user_id)
        if user_id in admins:
            old_username = admins[user_id]
            admins[user_id] = new_username
            bot.send_message(message.chat.id, f"Администратор {old_username} изменен на {new_username}.")
        else:
            bot.send_message(message.chat.id, "Администратор с таким ID не найден.")
    except ValueError:
        bot.send_message(message.chat.id, "Неправильный формат. Используйте: /change_admin user_id new_username")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")

@bot.message_handler(commands=['get_user_id'])
def get_user_id(message):
    try:
        # Команда должна быть в формате /get_user_id username
        _, username = message.text.split()
        chat_id = message.chat.id
        user = bot.get_chat_member(chat_id, username)
        user_id = user.user.id
        bot.send_message(chat_id, f"User ID for {username} is {user_id}")
    except ValueError:
        bot.send_message(message.chat.id, "Неправильный формат. Используйте: /get_user_id username")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")

def get_admins(chat_id):
    if admins:
        admin_list = [f"{admin_id}: {admin_name}" for admin_id, admin_name in admins.items()]
        admin_message = "Администраторы бота:\n" + "\n".join(admin_list)
    else:
        admin_message = "Список администраторов пуст."
    bot.send_message(chat_id, admin_message)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == '👋 Поздороваться':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)  # создание новых кнопок
        btn1 = types.KeyboardButton('Супер Админ')
        btn2 = types.KeyboardButton('Блюда')
        btn3 = types.KeyboardButton('Добавить блюдо')
        btn4 = types.KeyboardButton('Заказы')
        btn5 = types.KeyboardButton('Комментарии')
        btn6 = types.KeyboardButton('Помощь')

        markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
        bot.send_message(message.from_user.id, '❓ Задайте интересующий вопрос', reply_markup=markup)  # ответ бота
    elif message.text == 'Супер Админ':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn7 = types.KeyboardButton('Добавить администратора')
        btn8 = types.KeyboardButton('Изменить')
        markup.add(btn7, btn8)
        bot.send_message(message.from_user.id, 'Привет, Супер Админ, выбери что хочешь сделать', reply_markup=markup)
        get_admins(message.chat.id)
    elif message.text == 'Добавить администратора':
        bot.send_message(message.chat.id,
                         'Используйте команду /add_admin user_id username для добавления администратора.')
    elif message.text == 'Изменить':
        bot.send_message(message.chat.id,
                         'Используйте команду /change_admin user_id new_username для изменения администратора.')


if __name__ == "__main__":
    bot.infinity_polling(none_stop=True)
