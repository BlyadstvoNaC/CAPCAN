import telebot
from telebot import types
from KeyBoards import profileMP, MenuMP
from DBfunctions import db
from My.BotToken import token
import re
from Orders_functions import send_basket, query_handler, check_history
from Order import user_order_dict

user_data = {}
command_list = ['/start', '/profile', '/menu', '/basket', '/history', '/my_orders']

bot = telebot.TeleBot(token)

def is_valid_email(email):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None

@bot.message_handler(commands=['start', 'profile', 'menu', 'basket', 'history', 'my_orders'])
def handle_command(message):
    bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
    if message.text == '/start':
        if not db.is_registered(message.chat.id):
            regist(message)
        else:
            bot.send_message(message.chat.id, "Наше меню", reply_markup=MenuMP)
    elif message.text == '/profile':
        set_profile(message)
    elif message.text == '/menu':
        check_menu(message)
    elif message.text == '/history':
        check_history(message)
    elif message.text == '/my_orders':
        pass
    elif message.text == '/basket':
        send_basket(message.chat.id)
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
        msg = bot.send_message(message.chat.id, 'Введите номер телефона: (+375(код)*******)')
        bot.register_next_step_handler(msg, reg_tp_number)

def reg_tp_number(message):
    if message.text in command_list:
        bot.send_message(message.chat.id, "Сначала пройдите регистрацию:")
        msg = bot.send_message(message.chat.id, 'Введите номер телефона: (+375(код)*******)')
        bot.register_next_step_handler(msg, reg_tp_number)
    else:
        if len(message.text) == 13 and message.text[:4] == '+375' and message.text[4:6] in ['29', '33', '44', '25']:
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
        tmp_list = [message.from_user.id]
        for i in user_data[message.from_user.id]:
            tmp_list.append(i)
        db.new_client(tmp_list)
        tmp_list.clear()
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
    bot.answer_callback_query(callback_query_id=callback.id)
    data = callback.data[3:]
    if data == 'name':
        msg = bot.send_message(callback.message.chat.id, "Ввдеите новое имя:")
        bot.register_next_step_handler(msg, change_name)
    elif data == 'tp':
        msg = bot.send_message(callback.message.chat.id, "Ввeдите новый номер телефона (+375(код)*******)):")
        bot.register_next_step_handler(msg, change_tp)
    elif data == 'address':
        msg = bot.send_message(callback.message.chat.id, "Ввeдите новый адрес:")
        bot.register_next_step_handler(msg, change_address)
    elif data == 'email':
        msg = bot.send_message(callback.message.chat.id, "Ввeдите новый email:")
        bot.register_next_step_handler(msg, change_email)
    elif data == 'confirm':
        check_menu(callback.message)

def set_profile(message):
    tmp_user_list = db.get_client_data(message.from_user.id)
    bot.send_message(message.chat.id, f"Хотите изменить профиль? \n"
                                      f"Имя: {tmp_user_list[2]}\n"
                                      f"Телефон: {tmp_user_list[3]}\n"
                                      f"Email: {tmp_user_list[4]}\n"
                                      f"Адрес: {tmp_user_list[5]}\n", reply_markup=profileMP)

def change_name(message):
    name = message.text
    tmp_user_list = list(db.get_client_data(message.from_user.id))
    tmp_user_list[2] = name
    db.update_client_data(message.from_user.id, tmp_user_list[2:])
    set_profile(message)

def change_tp(message):
    if message.text == None:
        bot.send_message(message.chat.id, '' )
    elif len(message.text) == 13 and message.text[:4] == '+375' and message.text[4:6] in ['29', '33', '44', '25']:
        tp = message.text
        tmp_user_list = list(db.get_client_data(message.from_user.id))
        tmp_user_list[3] = tp
        db.update_client_data(message.from_user.id, tmp_user_list[2:])
        set_profile(message)
    else:
        msg = bot.send_message(message.chat.id, "Неверный номер телефона:")
        bot.register_next_step_handler(msg, change_tp)

def change_email(message):
    if is_valid_email(message.text):
        email = message.text
        tmp_user_list = list(db.get_client_data(message.from_user.id))
        tmp_user_list[4] = email
        db.update_client_data(message.from_user.id, tmp_user_list[2:])
        set_profile(message)
    else:
        msg = bot.send_message(message.chat.id, "Неверный адресс почты:")
        bot.register_next_step_handler(msg, change_email)

def change_address(message):
    addr = message.text
    tmp_user_list = list(db.get_client_data(message.from_user.id))
    tmp_user_list[5] = addr
    db.update_client_data(message.from_user.id, tmp_user_list[2:])
    set_profile(message)

#########################################################################################


#                                   БЛОК ВЫВОДА МЕНЮ                                    #
#########################################################################################

def check_menu(message):
    bot.send_message(message.chat.id, "Наше меню", reply_markup=MenuMP)

@bot.callback_query_handler(lambda callback: callback.data.startswith('men_'))
def check_dishes(callback):
    bot.answer_callback_query(callback_query_id=callback.id)
    data = callback.data[4:]
    if data == "basket":
        send_basket(callback.message.chat.id)
    else:
        markup = get_dishes_keyboard(data)
        bot.send_message(callback.message.chat.id, "Выбирите блюдо:", reply_markup=markup)

def get_dishes_keyboard(category):
    dishesMP = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    for i in db.menu_data_on_category(category):
        button = types.KeyboardButton(f"{i[1]}")
        dishesMP.add(button)
    return dishesMP

def generate_order_keyb(cnt, name):
    dishMP = types.InlineKeyboardMarkup(row_width=3)
    buttonPlus = types.InlineKeyboardButton("+", callback_data='ds_+')
    buttonMinus = types.InlineKeyboardButton("-", callback_data='ds_-')
    buttonCount = types.InlineKeyboardButton(f"{name} {cnt}", callback_data='ds_cnt')
    buttonBasket = types.InlineKeyboardButton("Добавить в корзину", callback_data='ds_bask')
    buttonMenu = types.InlineKeyboardButton("вернуться в меню", callback_data='ds_menu')
    buttonRSwipe = types.InlineKeyboardButton("⏩", callback_data='ds_r')
    buttonLSwipe = types.InlineKeyboardButton("⏪", callback_data='ds_l')
    buttonCont = types.InlineKeyboardButton("Продолжить", callback_data='ds_next')
    dishMP.add(buttonMinus, buttonCount, buttonPlus, buttonLSwipe, buttonMenu, buttonRSwipe, buttonBasket, buttonCont)
    return dishMP

@bot.message_handler(content_types=['text'])
def dish_info(message):
    tmp = db.dish_data_on_name(message.text)
    bot.send_photo(message.chat.id, photo=open(tmp[5], 'rb'), caption=f'{tmp[1]}',
                   reply_markup=generate_order_keyb(1, str(tmp[1])))

@bot.callback_query_handler(lambda callback: callback.data.startswith('ds_'))
def make_order(callback):
    bot.answer_callback_query(callback_query_id=callback.id)
    data = callback.data[3:]
    if data == 'menu':
        check_menu(callback.message)
    elif data == 'bask':
        tmp = db.dish_data_on_name(check_name(callback))
        user_id = check_user_id(callback)
        dish = (tmp[0], tmp[1], check_count(callback), tmp[4])
        if user_id not in user_order_dict.keys():
            user_order_dict.update({user_id : [dish]})
        else:
            user_order_dict[user_id].append(dish)
    elif data == '+':
        cnt = check_count(callback)+1
        name = str(check_name(callback))
        murkup = generate_order_keyb(cnt, name)
        bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                      reply_markup=murkup)
    elif data == '-':
        cnt = check_count(callback)
        if cnt > 1:
            cnt -= 1
            name = str(check_name(callback))
            murkup = generate_order_keyb(cnt, name)
            bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                          reply_markup=murkup)
    elif data == 'cnt':
        pass
    elif data == 'r':
        dish_id = int(db.dish_data_on_name(check_name(callback))[0]) + 1
        if not db.dish_data_on_id(dish_id):
            pass
        else:
            inf = db.dish_data_on_id(dish_id)
            new_media = types.InputMediaPhoto(media=open(f'{inf[5]}','rb'), caption=f"{inf[1]}")
            bot.edit_message_media(
                    media=new_media,
                    chat_id=callback.message.chat.id,
                    message_id=callback.message.message_id,
                    reply_markup=generate_order_keyb(1, inf[1])
                )
    elif data == 'l':
        dish_id = int(db.dish_data_on_name(check_name(callback))[0]) - 1
        if not db.dish_data_on_id(dish_id):
            pass
        else:
            inf = db.dish_data_on_id(dish_id)
            new_media = types.InputMediaPhoto(media=open(f'{inf[5]}', 'rb'), caption=f"{inf[1]}")
            bot.edit_message_media(
                media=new_media,
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                reply_markup=generate_order_keyb(1, inf[1]))
    elif data == 'next':
        send_basket(callback.message.chat.id)

def check_name(callback):
    mess = callback.message.json
    dish = re.findall(r'[a-zA-Zа-яА-Я-]', mess['reply_markup']['inline_keyboard'][0][1]['text'])
    dish_name = ''
    for _ in dish:
        dish_name += _
    return dish_name

def check_count(callback):
    mess = callback.message.json
    dish = re.findall(r'[0-9]', mess['reply_markup']['inline_keyboard'][0][1]['text'])
    dish_count = ''
    for _ in dish:
        dish_count += _
    return int(dish_count)

def check_user_id(callback):
    mess = callback.message.json
    return mess['chat']['id']

#########################################################################################


#                                   БЛОК ВЫВОДА ИСТОРИИ                                 #
#########################################################################################
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    bot.answer_callback_query(callback_query_id=call.id)
    query_handler(call)
#########################################################################################

bot.infinity_polling()