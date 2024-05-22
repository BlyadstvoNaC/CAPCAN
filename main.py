import telebot
from telebot import types
from IgorFuntions import is_valid_email
from Peremen import user_data, token, command_list
from DBfunctions import db

bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start', 'profile', 'menu', 'basket', 'history', 'my_orders'])
def handle_command(message):
    bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
    if message.text == '/start':
        if db.is_registered(message.chat.id):
            regist(message)
        #проверка id через функцию Оли(возвращает true или false)
        #регистрируем пользователя
        else:
            pass # вызываем меню

    elif message.text == '/profile':
        set_profile(message)

#                                   БЛОК РЕГИСТРАЦИИ                                    #
#########################################################################################
def regist(message):
    bot.send_message(message.chat.id, "Добро пожаловать в бот *****"
                                      "Пожалуйста предоставьте данные для регистрации")
    msg = bot.send_message(message.chat.id, "Как вас зовут:")
    bot.register_next_step_handler(msg, reg_name)


def reg_name(message):
    if message.text in command_list:
        bot.send_message(message.chat.id, "Сначала пройдите регистрацию:")
        msg = bot.send_message(message.chat.id, "Как вас зовут:")
        bot.register_next_step_handler(msg, reg_name)
    else:
        user_data.update({message.from_user.id: [message.text]})
        msg = bot.send_message(message.chat.id, 'Как мы можем с вами связаться?')
        bot.register_next_step_handler(msg, reg_tp_number)


def reg_tp_number(message):
    if message.text in command_list:
        bot.send_message(message.chat.id, "Сначала пройдите регистрацию:")
        msg = bot.send_message(message.chat.id, 'Как мы можем с вами связаться?')
        bot.register_next_step_handler(msg, reg_tp_number)
    else:
        if len(message.text) == 13 and message.text[:4] == '+375' and message.text[4:6] in ['29', '33', '44']:
            user_data[message.from_user.id].append(message.text)
            msg = bot.send_message(message.chat.id, 'Какой у вас адрес?')
            bot.register_next_step_handler(msg, reg_address)
        else:
            msg = bot.send_message(message.chat.id, 'Неверный номер, попробуйте еще раз')
            bot.register_next_step_handler(msg, reg_tp_number)

#поменять местами
def reg_address(message):
    if message.text in command_list:
        bot.send_message(message.chat.id, "Сначала пройдите регистрацию:")
        msg = bot.send_message(message.chat.id, 'Какой у вас адрес?')
        bot.register_next_step_handler(msg, reg_address)
    else:
        user_data[message.from_user.id].append(message.text)
        msg = bot.send_message(message.chat.id, 'Укажите ваш email?')
        bot.register_next_step_handler(msg, reg_email)

def reg_email(message):
    if message.text in command_list:
        bot.send_message(message.chat.id, "Сначала пройдите регистрацию:")
        msg = bot.send_message(message.chat.id, 'Укажите ваш email?')
        bot.register_next_step_handler(msg, reg_email)
    else:
        if is_valid_email(message.text):
            user_data[message.from_user.id].append(message.text)
            bot.send_message(message.chat.id, 'Спасибо за регистрацию!')
            print(user_data)
            set_profile(message)
        else:
            msg = bot.send_message(message.chat.id, 'Неверный паттерн почты, попробуйте еще раз')
            bot.register_next_step_handler(msg, reg_email)

#########################################################################################


#                                   БЛОК ИЗМЕНЕНИЯ ПРОФИЛЯ                              #
#########################################################################################
@bot.callback_query_handler(lambda callback: callback.data.startswith('pr_'))
def change_profile(callback):
    data = callback.data[3:]
    if data == 'name':
        print("Изменить время")
    elif data == 'tp':
        pass
    elif data == 'address':
        pass
    elif data == 'email':
        pass
    elif data == 'confirm':
        pass

def set_profile(message):

    #клавиатура постоянная, поэтому можно в переменные
    profileMP = types.InlineKeyboardMarkup(row_width=1)
    name_button = types.InlineKeyboardButton("Изменить имя", callback_data="pr_name")
    tp_button = types.InlineKeyboardButton("Изменить телефон", callback_data="pr_tp")
    address_button = types.InlineKeyboardButton("Изменить адрес", callback_data="pr_address")
    email_button = types.InlineKeyboardButton("Изменить почту", callback_data="pr_email")
    confirm_button = types.InlineKeyboardButton("Продолжить", callback_data="pr_confirm")

    profileMP.add(name_button, tp_button, address_button, email_button, confirm_button)

    bot.send_message(message.chat.id, f"Хотите изменить профиль? \n"
                                       f"Имя: \n"
                                      f"Телефон: \n"
                                      f"Адрес: \n"
                                      f"Email: \n", reply_markup=profileMP)


#########################################################################################

bot.infinity_polling()
