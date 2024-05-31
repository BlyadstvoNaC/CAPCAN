import telebot
from KeyBoards import profileMP
from DBfunctions import db
from My.BotToken import token
import re


user_data = {}
command_list = ['/start', '/profile', '/menu', '/basket', '/history', '/my_orders']

bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start', 'profile', 'menu', 'basket', 'history', 'my_orders'])
def handle_command(message):
    bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
    if message.text == '/start':
        if db.is_registered(message.chat.id) == False:
            regist(message)
        else:
            print('menu')
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
            msg = bot.send_message(message.chat.id, 'Какой у вас email?')
            bot.register_next_step_handler(msg, reg_email)
        else:
            msg = bot.send_message(message.chat.id, 'Неверный номер, попробуйте еще раз')
            bot.register_next_step_handler(msg, reg_tp_number)


def reg_address(message):
    if message.text in command_list:
        bot.send_message(message.chat.id, "Сначала пройдите регистрацию:")
        msg = bot.send_message(message.chat.id, 'Какой у вас адрес?')
        bot.register_next_step_handler(msg, reg_address)
    else:
        user_data[message.from_user.id].append(message.text)
        bot.send_message(message.chat.id, 'Спасибо за регистрацию!')
        tmp_list = []
        tmp_list.append(message.from_user.id)
        for i in user_data[message.from_user.id]:
            tmp_list.append(i)
        print(tmp_list)
        tmp_list.clear()
        db.new_client(tmp_list)

        set_profile(message)

def reg_email(message):
    if message.text in command_list:
        bot.send_message(message.chat.id, "Сначала пройдите регистрацию:")
        msg = bot.send_message(message.chat.id, 'Укажите ваш email?')
        bot.register_next_step_handler(msg, reg_email)
    else:
        if is_valid_email(message.text):
            user_data[message.from_user.id].append(message.text)
            msg = bot.send_message(message.chat.id, 'Укажите ваш адрес.')
            bot.register_next_step_handler(msg, reg_address)
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
        msg = bot.send_message(callback.message.chat.id,"Ввдеите имя:")
        bot.register_next_step_handler(msg, change_name)
    elif data == 'tp':
        pass
    elif data == 'address':
        pass
    elif data == 'email':
        pass
    elif data == 'confirm':
        pass

def set_profile(message):
    tmp_user_list = db.get_client_data(message.from_user.id)
    bot.send_message(message.chat.id, f"Хотите изменить профиль? \n"
                                       f"Имя: {tmp_user_list[2]}\n"
                                      f"Телефон: {tmp_user_list[3]}\n"
                                      f"Email: {tmp_user_list[4]}\n"
                                      f"Адрес: {tmp_user_list[5]}\n", reply_markup=profileMP)

def change_name(message):
    pass


#########################################################################################

def is_valid_email(email):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None

bot.infinity_polling()
