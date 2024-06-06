import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# from Bot_Dishes.Client_functions import user_order_dict
from My import Bot_Food_Token
from DBfunctions import db
from Sheduler import schedule_message, start_scheduler_thread
import logging
import time
import threading

logging.basicConfig(level=logging.INFO)

bot = telebot.TeleBot(Bot_Food_Token.token)

# """кнопки Help, заказ подтвержден, сколько времени осталось?"""
# markupH = types.ReplyKeyboardMarkup(resize_keyboard=True)
# button_1 = types.KeyboardButton('Help')
# button_2 = types.KeyboardButton('Заказ подтвержден')
# button_3 = types.KeyboardButton('Сколько времени осталось?')
# markupH.add(button_1)
# markupH.add(button_2)
# markupH.add(button_3)

markupH = types.InlineKeyboardMarkup()
button_1 = types.InlineKeyboardButton('Help', callback_data='help')
button_2 = types.InlineKeyboardButton('Заказ подтвержден', callback_data='order')
button_3 = types.InlineKeyboardButton('Сколько времени осталось?', callback_data='time')
markupH.add(button_1)
markupH.add(button_2)
markupH.add(button_3)
#
# """кнопки для basket?"""
# markupB = types.ReplyKeyboardMarkup(resize_keyboard=True)
# button_1 = types.KeyboardButton('Изменить')
# button_2 = types.KeyboardButton('Продолжить')
# markupB.add(button_1)
# markupB.add(button_2)

# """кнопки для изменения basket?"""
# markupUB = types.ReplyKeyboardMarkup(resize_keyboard=True)
# button_1 = types.KeyboardButton('🗑')
# button_2 = types.KeyboardButton('-')
# button_3 = types.KeyboardButton('Блюдо')
# button_4 = types.KeyboardButton('+')
# markupUB.add(button_1, button_2, button_3, button_4)

# """кнопка для подтверждения basket?"""
# markupPb = types.ReplyKeyboardMarkup(resize_keyboard=True)
# button_1 = types.KeyboardButton('Подтвердить')
# markupPb.add(button_1)


my_dict_orders = {"user_tg_chat_id": [(1, 'Пицца', 1, 20), (2, 'Омлет', 1, 17), (3, 'Фо-бо', 1, 33), ]}
"""заполнить чем-то для проверки на наличие текущего заказа"""
# user_order_dict = {message.chat.id: [(1, 'Пицца', 1, 20), (2, 'Омлет', 1, 17), (3, 'Фо-бо', 1, 33), ]}

order_schedule_times = {}
"""Функция получения истории заказов из БД и перевод их в список [номер заказа-дата](вроде?).
На вход принимается история заказов из БД по Ольгиной функции в виде списка кортежей. Что ж за жизнь, то такая?"""


def history_orders(data):
    list_history_orders = []

    for index, history in enumerate(data_history):
        """взять из Оленой функции набор с заказами и вывести их по одному: заказ номер - дата"""
        res_hystory = f'{history[0]} - {history[3]}'
        list_history_orders.append(res_hystory)
    return list_history_orders


"""Функция для вычисления максимального времени приготовления блюда"""
# список id блюд из корзины для получения времени готовки. Наверное передать Ольге и у нее получить как-то список?
id_dishes_orders = [id_dish[0] for id_dish in my_dict_orders["user_tg_chat_id"]]
# id_dishes_orders = [id_dish[0] for id_dish in user_order_dict[message.chat.id]]

# затем этот список или что-то передать в get_max_cooking_time

def get_max_cooking_time(orders):
    return max(dish[3] for dish in orders) if orders else 0


"""инлайн-кнопки, для истории заказов?"""
# data_history = db.orders_history(message.chat.id)
# data_history = db.orders_history('3fdf5g544')  # Тест
"""тест для истории заказов?"""
data_history = [(1, 1, 1, '20240519 15:40:00', 50, 'г Минск, пр Держинского 154'),
                (2, 1, 1, '20240519 16:40:00', 50, 'г Минск, пр Держинского 84'),
                (3, 1, 1, '20240519 17:40:00', 50, 'г Минск, пр Держинского 154'),
                (4, 1, 1, '20240519 18:40:00', 50, 'г Минск, пр Держинского 15'),
                (5, 1, 1, '20240519 19:40:00', 50, 'г Минск, пр Держинского 54'),
                (6, 1, 1, '20240519 20:40:00', 50, 'г Минск, пр Держинского 14')]  # Тест

print(history_orders(data_history))

"""Функция `generate_markup(page)` создает клавиатуру с кнопками для навигации по страницам"""


def generate_markup(page):
    markup = InlineKeyboardMarkup(row_width=1)
    start_index = page * 2  # изменение цифры выводимых заказов
    end_index = start_index + 2  # изменение цифры выводимых заказов
    for item in history_orders(data_history)[start_index:end_index]:
        markup.add(InlineKeyboardButton(item, callback_data="m" + f'{item}'))
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("<<<", callback_data='<' + f'{page - 1}'))
    if end_index < len(history_orders(data_history)):
        nav_buttons.append(InlineKeyboardButton(">>>", callback_data='>' + f'{page + 1}'))
    markup.row(*nav_buttons)
    return markup


def start(message):
    if message.text == '/my_orders':
        # """проверка на наличие текущего заказа"""
        # if my_dict_orders["user_tg_chat_id"]:
        bot.send_message(message.chat.id, "Текущий заказ ⬇️")
        """выводим данные о клиенте?"""
        """взять их из БД? Вывели"""
        # data_my_order = db.my_orders(message.chat.id)
        # data_my_client = db.get_client_data(message.chat.id)
        # data_dishes_my_order = db.dishes_data(history[0])
        data_my_order = db.my_orders('nfj4j3nj4')  # Тест
        data_my_client = db.get_client_data('nfj4j3nj4')  # Тест
        data_dishes_my_order = db.dishes_data(1)  # Тест

        """данные клиента по заказу: имя, телефон, почта, адрес"""
        """Выводим кнопки"""
        # for user in data_my_client:
        data_user = f'{data_my_client[2]}\n{data_my_client[3]}\n{data_my_client[4]}\n{data_my_client[5]}'
        bot.send_message(message.chat.id, "Данные о клиенте")
        bot.send_message(message.chat.id, data_user)

        print(data_my_order)
        print(data_my_client)
        print(data_dishes_my_order)
        """выводим список блюд (тоже из бд или из корзины)?"""
        """взять их из откуда(БД)?"""
        bot.send_message(message.chat.id, "Список блюд и общая сумма заказа:")
        res_sum = 0
        res_dish_hist = ''
        for dish in data_dishes_my_order:
            res_dish_hist += f'{dish[1]}\n'
            res_sum += dish[2] * dish[3]
        bot.send_message(message.chat.id, res_dish_hist)
        bot.send_message(message.chat.id, (str(res_sum) + " руб."), reply_markup=markupH)

    # elif message.text == 'Help':
    #     bot.send_message(message.chat.id, "Позвонить ответственному лицу или кому-то там по телефону +375296333111")

    # elif message.text == 'Заказ подтвержден':
    #     # data_my_order = db.my_orders(message.chat.id)
    #     # data_my_client = db.get_client_data(message.chat.id)
    #     data_my_order = db.my_orders('nfj4j3nj4')  # Тест
    #     data_my_client = db.get_client_data('nfj4j3nj4')  # Тест
    #     """проверка на из-деливерид?"""
    #     if data_my_order[0][2] == 0:
    #         bot.send_message(message.chat.id, "Доставлен ли заказ? Оставьте, пожалуйста, комментарий: ГДЕ?")
    #
    #     elif data_my_order[0][2] == 1:
    #         bot.send_message(message.chat.id, "Заказ завершен")

    # elif message.text == 'Сколько времени осталось?':
    #     bot.send_message(message.chat.id, "Ждем шедулера? Бесконечность - это не предел...?")

    if message.text == '/history':
        bot.send_message(
            message.chat.id, "Список завершенных заказов.",
        )
        bot.send_message(
            message.chat.id, "Выберите один из заказов ⬇️:",
            reply_markup=generate_markup(0)
        )

    # x = ['a', 'b', 'c', 'd', 'e', 'w', 'df', 'ww', 'x', 'qa', 'wsx']
    #
    # for i in range(0, len(x), 3):
    #     input('Введи "go" ')
    #     print(x[i: i + 3])
    # print('Выход из цикла')

    # if message.text == '/basket':
    #     # user_dict[message.chat.id] += message.text
    #     if my_dict_orders["user_tg_chat_id"]:
    #         bot.send_message(
    #             message.chat.id, "Список блюд c ценой и общая сумма заказа в корзине 🥰:",
    #             reply_markup=markupB
    #         )
    #         """функция вывода списка блюд c ценой и общей суммой заказа в корзине"""
    #
    #         # list_dishes_price_basket(my_dict_orders["user_tg_chat_id"])
    #         res_sum_bask = 0
    #         # res_dish_bask = ''
    #         for dish_bask in my_dict_orders["user_tg_chat_id"]:
    #             print(dish_bask)
    #             res_dish_bask = f'Блюдо {dish_bask[1]} {dish_bask[3]} - {dish_bask[2]} - {dish_bask[2] * dish_bask[3]}'
    #             res_sum_bask += dish_bask[2] * dish_bask[3]
    #             bot.send_message(message.chat.id, res_dish_bask)
    #         bot.send_message(message.chat.id, (str(res_sum_bask) + " руб."))
    #
    #     else:
    #         bot.send_message(message.chat.id, "Basket пустая!", reply_markup=None)
    #
    # elif message.text == 'Изменить':
    #
    #     markupUB = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    #     """кнопки для изменения basket?"""
    #     for ind_but, dish_but in enumerate(my_dict_orders["user_tg_chat_id"]):
    #         print(dish_but)
    #         res_upd_dish_bask = f'{dish_but[1]} - {dish_but[2]}'
    #
    #         button_1 = types.KeyboardButton('🗑')
    #         button_2 = types.KeyboardButton('-')
    #         button_3 = types.KeyboardButton(res_upd_dish_bask)
    #         button_4 = types.KeyboardButton('+')
    #         markupUB.add(button_1, button_2, button_3, button_4)
    #
    #     bot.send_message(
    #         message.chat.id, "Список блюд для изменения заказа в корзине 🥰:",
    #         reply_markup=markupUB
    #     )
    #
    #     """функция вывода списка блюд c ценой и общей суммой заказа в корзине"""
    #     res_sum_bask = 0
    #     # res_dish_bask = ''
    #     for dish_bask in my_dict_orders["user_tg_chat_id"]:
    #         print(dish_bask)
    #         res_dish_bask = f'Блюдо {dish_bask[1]} {dish_bask[3]} - {dish_bask[2]} - {dish_bask[2] * dish_bask[3]}'
    #         res_sum_bask += dish_bask[2] * dish_bask[3]
    #         bot.send_message(message.chat.id, res_dish_bask)
    #     bot.send_message(message.chat.id, (str(res_sum_bask) + " руб."))
    #
    #     """выведение реализации кнопок в разделе изменения заказа"""
    # # elif message.text == '🗑':
    #
    # elif message.text == 'Продолжить':
    #
    #     bot.send_message(message.chat.id, "Неизвестный пока /profile 🥰")
    #     """Проверка зарегистрирован ли пользователь"""
    #     # if db.is_registered(message.chat.id):
    #     if db.is_registered('3fdf5g544'):
    #         """выводим данные о клиенте?"""
    #         """взять их из БД? Вывели"""
    #
    #         # data_my_client = db.get_client_data(message.chat.id)
    #         data_my_order = db.my_orders('3fdf5g544')  # Тест
    #         data_my_client = db.get_client_data('3fdf5g544')  # Тест
    #         data_dishes_my_order = db.dishes_data(1)  # Тест
    #
    #         """данные клиента по заказу: имя, телефон, почта, адрес"""
    #         """Выводим кнопки"""
    #         # for user in data_my_client:
    #         data_user = f'{data_my_client[2]}\n{data_my_client[3]}\n{data_my_client[4]}\n{data_my_client[5]}'
    #         bot.send_message(message.chat.id, "Данные о клиенте")
    #         bot.send_message(message.chat.id, data_user, reply_markup=markupPb)
    #
    #         print(data_my_client)
    #         print(data_dishes_my_order)
    #         """выводим список блюд (из корзины)?"""
    #         """взять их из откуда(basket)?"""
    #         bot.send_message(message.chat.id, "Список блюд и общая сумма заказа:")
    #
    #         res_sum_bask = 0
    #         res_dish_bask = ''
    #         for dish_bask in my_dict_orders["user_tg_chat_id"]:
    #             print(dish_bask)
    #             # res_dish_bask = f'{dish_bask[1]}'
    #             res_dish_bask += f'{dish_bask[1]}\n'
    #             res_sum_bask += dish_bask[2] * dish_bask[3]
    #             # bot.send_message(message.chat.id, res_dish_bask)
    #         bot.send_message(message.chat.id, res_dish_bask)
    #         bot.send_message(message.chat.id, (str(res_sum_bask) + " руб."))
    #
    # elif message.text == 'Подтвердить':
    #
    #     bot.send_message(message.chat.id, "Заказ активен ушел в БД и пошел готовиться")
    #     """Далее должна быть какая-то функция подтверждения от Мирослава и Влада"""
    #     bot.send_message(message.chat.id, "Ждем какую-то функцию подтверждения от Мирослава и Влада")
    #
    #     """Нужна какая-то реализация отложенного сообщения"""
    #     bot.send_message(message.chat.id,
    #                      "Отложенное сообщение на id клиента через время готовки макс блюда + 30 минут. Реализация?")
    #
    #     bot.send_message(message.chat.id, "Доставлен ли заказ? Оставьте, пожалуйста, комментарий: ГДЕ?")

    if message.text == '/basket':
        send_basket(message.chat.id)

    elif message.text == 'Подтвердить':
        confirm_order(message)

    # elif message.text == 'Подтвердить':
    #     bot.send_message(message.chat.id, "Заказ активен ушел в БД и пошел готовиться")
    #     bot.send_message(message.chat.id, "Ждем какую-то функцию подтверждения от Мирослава и Влада")
    #     bot.send_message(message.chat.id,
    #                      "Отложенное сообщение на id клиента через время готовки макс блюда + 30 минут. Реализация?")
    #     bot.send_message(message.chat.id, "Доставлен ли заказ? Оставьте, пожалуйста, комментарий: ГДЕ?")

    """функция send_basket, которая отображает корзину и выводит ее содержимое с инлайн-кнопками"""


def send_basket(chat_id):
    # if user_order_dict[message.chat.id]:
    if my_dict_orders["user_tg_chat_id"]:
        markupB = InlineKeyboardMarkup(row_width=2)
        button_1 = InlineKeyboardButton('Изменить', callback_data='change')
        button_2 = InlineKeyboardButton('Продолжить', callback_data='continue')
        markupB.add(button_1, button_2)

        res_sum_bask = 0
        res_dish_bask = ''
        # for dish_bask in user_order_dict[message.chat.id]:
        for dish_bask in my_dict_orders["user_tg_chat_id"]:
            res_dish_bask += f'Блюдо {dish_bask[1]} {dish_bask[3]} - {dish_bask[2]} - {dish_bask[2] * dish_bask[3]}\n'
            res_sum_bask += dish_bask[2] * dish_bask[3]

        bot.send_message(chat_id,
                         f"Список блюд c ценой и общая сумма заказа в корзине 🥰:\n{res_dish_bask}{res_sum_bask} руб.",
                         reply_markup=markupB)
    else:
        bot.send_message(chat_id, "Basket пустая!", reply_markup=None)


def confirm_order(message):
    bot.send_message(message.chat.id, "Заказ активен ушел в БД и пошел готовиться")
    bot.send_message(message.chat.id, "Ждем какую-то функцию подтверждения от Мирослава и Влада")
    bot.send_message(message.chat.id,
                     "Отложенное сообщение на id клиента будет отправлено через время готовки макс блюда + 30 минут.")
    # bot.send_message(message.chat.id, "Доставлен ли заказ? Оставьте, пожалуйста, комментарий: ГДЕ?")

    # max_cooking_time = get_max_cooking_time(user_order_dict[message.chat.id]) ?
    max_cooking_time = get_max_cooking_time(my_dict_orders["user_tg_chat_id"])
    # delay = max_cooking_time + 30 * 60  # добавляем 30 минут к максимальному времени готовки
    delay = max_cooking_time + 1 * 60  # Тест добавляем 1 минут к максимальному времени готовки
    schedule_time = time.time() + delay

    # Планируем отправку отложенного сообщения
    schedule_message(bot, message.chat.id, "Ваш заказ готов и отправлен. Спасибо за ожидание!"
                                           "Оставьте, пожалуйста, комментарий: ГДЕ?", delay)

    # Сохраняем время отправки
    order_schedule_times[message.chat.id] = schedule_time
    print(order_schedule_times)

    # Добавляем кнопку для отслеживания времени
    markupPb = types.InlineKeyboardMarkup(row_width=1)
    button_1 = types.InlineKeyboardButton('Подтвердить', callback_data='confirm')
    button_2 = types.InlineKeyboardButton('Отследить время', callback_data='track_time')
    markupPb.add(button_1, button_2)
    bot.send_message(message.chat.id, "Что вы хотите сделать дальше?", reply_markup=markupPb)


def track_time(chat_id):
    if chat_id in order_schedule_times:
        remaining_time = order_schedule_times[chat_id] - time.time()
        if remaining_time > 0:
            minutes, seconds = divmod(remaining_time, 60)
            bot.send_message(chat_id,
                             f"Оставшееся время до отправки заказа: {int(minutes)} минут и {int(seconds)} секунд.")
        else:
            bot.send_message(chat_id, "Заказ уже отправлен.")
    else:
        bot.send_message(chat_id, "Время для этого заказа не установлено.")


def query_handler(call):
    bot.answer_callback_query(callback_query_id=call.id, )
    flag = call.data[0]
    data = call.data[1:]
    if flag == "m":
        bot.send_message(call.message.chat.id, f"Выбранный из истории заказ ⬇️:  {data}")
        """выводим данные о клиенте?"""
        """взять их из БД? Вывели"""
        # data_my_order_hist = db.my_orders(message.chat.id)
        # data_my_client_hist = db.get_client_data(message.chat.id)
        # data_dishes_hist = db.dishes_data(history[0])
        data_my_client_hist = db.get_client_data('3fdf5g544')  # Тест
        data_dishes_hist = db.dishes_data(1)  # Тест

        """данные клиента по заказу: имя, телефон, почта, адрес"""
        # for user in data_my_client:
        data_user = f'{data_my_client_hist[2]}\n{data_my_client_hist[3]}\n{data_my_client_hist[4]}\n{data_my_client_hist[5]}'
        bot.send_message(call.message.chat.id, "Данные о клиенте:")
        bot.send_message(call.message.chat.id, data_user)

        print(data_my_client_hist)
        print(data_dishes_hist)
        """выводим список блюд (тоже из бд или из корзины)?"""
        """взять их из откуда(БД)?"""
        """НЕ Выводим кнопки"""
        bot.send_message(call.message.chat.id, f"Список блюд и общая сумма выбранного заказа ⬇️:   {data}")
        res_sum = 0
        res_dish_hist = ''
        for dish in data_dishes_hist:
            res_dish_hist += f'{dish[1]}\n'
            res_sum += dish[2] * dish[3]
        bot.send_message(call.message.chat.id, res_dish_hist)
        bot.send_message(call.message.chat.id, (str(res_sum) + " руб."))

    elif flag == "<" or flag == ">":
        page = int(data)

        bot.edit_message_text("Выберите один из заказов ⬇️", call.message.chat.id, call.message.message_id,
                              reply_markup=generate_markup(page))

    elif flag == "h":
        # Обработка команды Help
        bot.send_message(call.message.chat.id,
                         "Позвонить ответственному лицу или кому-то там по телефону +375296333111."
                         "Позвони мне, позвони!")

    elif flag == "o":
        # Обработка команды Заказ подтвержден
        # data_my_order = db.my_orders(message.chat.id)
        # data_my_client = db.get_client_data(message.chat.id)
        data_my_order = db.my_orders('nfj4j3nj4')  # Тест

        """проверка на из-деливерид?"""
        if data_my_order[0][2] == 0:
            bot.send_message(call.message.chat.id, "Доставлен ли заказ? Оставьте, пожалуйста, комментарий: ГДЕ?")

        elif data_my_order[0][2] == 1:
            bot.send_message(call.message.chat.id, "Заказ завершен")

    elif flag == "t":
        # Обработка команды Сколько времени осталось?
        bot.send_message(call.message.chat.id,
                         "Ждем шедулера? Бесконечность - это не предел...?")

    # elif call.data == 'help_command':
    #
    #     bot.send_message(call.message.chat.id,
    #                      "Позвонить ответственному лицу или кому-то там по телефону +375296333111. Позвони мне, "
    #                      "позвони!")
    # elif call.data == 'order_confirmed_command':
    #     # Обработка команды Заказ подтвержден
    #     bot.send_message(call.message.chat.id, "Вы выбрали 'Заказ подтвержден'.")
    # elif call.data == 'time_left_command':
    #     # Обработка команды Сколько времени осталось?
    #     bot.send_message(call.message.chat.id, "Вы выбрали 'Сколько времени осталось?'.")

    """кнопки для изменения basket?"""
    if call.data == 'change':
        markupUB = InlineKeyboardMarkup(row_width=4)
        # for ind_but, dish_but in enumerate(user_order_dict[message.chat.id]):
        for ind_but, dish_but in enumerate(my_dict_orders["user_tg_chat_id"]):
            res_upd_dish_bask = f'{dish_but[1]} - {dish_but[2]}'
            button_1 = InlineKeyboardButton('🗑', callback_data=f'delete_{dish_but[0]}')
            button_2 = InlineKeyboardButton('-', callback_data=f'decrease_{dish_but[0]}')
            button_3 = InlineKeyboardButton(res_upd_dish_bask, callback_data=f'info_{dish_but[0]}')
            button_4 = InlineKeyboardButton('+', callback_data=f'increase_{dish_but[0]}')
            markupUB.add(button_1, button_2, button_3, button_4)

        button_check = InlineKeyboardButton('Подтвердить изменения', callback_data='check')
        markupUB.add(button_check)

        bot.send_message(call.message.chat.id, "Список блюд для изменения заказа в корзине 🥰:", reply_markup=markupUB)

    elif call.data == 'continue':
        """Проверка зарегистрирован ли пользователь"""
        # if db.is_registered(message.chat.id):
        if db.is_registered('3fdf5g544'):
            """выводим данные о клиенте?"""
            """взять их из БД? Вывели"""

            # data_my_client = db.get_client_data(message.chat.id)
            data_my_client = db.get_client_data('3fdf5g544')
            data_my_order = db.my_orders('3fdf5g544')
            data_dishes_my_order = db.dishes_data(1)

            data_user = f'{data_my_client[2]}\n{data_my_client[3]}\n{data_my_client[4]}\n{data_my_client[5]}'
            markupPb = InlineKeyboardMarkup(row_width=1)
            button_1 = InlineKeyboardButton('Подтвердить', callback_data='confirm')
            markupPb.add(button_1)

            bot.send_message(call.message.chat.id, "Данные о клиенте")
            bot.send_message(call.message.chat.id, data_user)

            """функция вывода списка блюд c ценой и общей суммой заказа в корзине"""
            res_sum_bask = 0
            res_dish_bask = ''
            # for dish_bask in user_order_dict[message.chat.id]:
            for dish_bask in my_dict_orders["user_tg_chat_id"]:
                res_dish_bask += f'{dish_bask[1]}\n'
                res_sum_bask += dish_bask[2] * dish_bask[3]

            bot.send_message(call.message.chat.id,
                             f"Список блюд и общая сумма заказа:\n{res_dish_bask}{res_sum_bask} руб.",
                             reply_markup=markupPb)

        """функция удаления блюда в корзине"""
    elif call.data.startswith('delete_'):
        dish_id = int(call.data.split('_')[1])
        # user_order_dict[message.chat.id] = [dish for dish in user_order_dict[message.chat.id] if dish[0] != dish_id]
        my_dict_orders["user_tg_chat_id"] = [dish for dish in my_dict_orders["user_tg_chat_id"] if dish[0] != dish_id]
        bot.send_message(call.message.chat.id, "Блюдо удалено из корзины.")
        print(my_dict_orders["user_tg_chat_id"])
        send_basket(call.message.chat.id)

        """функция уменьшения кол-ва блюд в корзине"""
    elif call.data.startswith('decrease_'):
        dish_id = int(call.data.split('_')[1])
        # for i, dish in enumerate(user_order_dict[message.chat.id]):
        for i, dish in enumerate(my_dict_orders["user_tg_chat_id"]):
            if dish[0] == dish_id:
                if dish[2] > 1:
                    dish_list = list(dish)
                    dish_list[2] -= 1
                    # user_order_dict[message.chat.id][i] = tuple(dish_list)
                    my_dict_orders["user_tg_chat_id"][i] = tuple(dish_list)
                else:
                    # user_order_dict[message.chat.id].pop(i)
                    my_dict_orders["user_tg_chat_id"].pop(i)
                break
        bot.send_message(call.message.chat.id, "Количество блюда уменьшено.")
        print(my_dict_orders["user_tg_chat_id"])
        send_basket(call.message.chat.id)

        """функция добавления кол-ва блюд в корзине"""
    elif call.data.startswith('increase_'):
        dish_id = int(call.data.split('_')[1])
        # for i, dish in enumerate(user_order_dict[message.chat.id]:
        for i, dish in enumerate(my_dict_orders["user_tg_chat_id"]):
            if dish[0] == dish_id:
                dish_list = list(dish)
                dish_list[2] += 1
                # user_order_dict[message.chat.id][i] = tuple(dish_list)
                my_dict_orders["user_tg_chat_id"][i] = tuple(dish_list)
                break
        bot.send_message(call.message.chat.id, "Количество блюда увеличено.")
        print(my_dict_orders["user_tg_chat_id"])
        send_basket(call.message.chat.id)

        """обработчик check в query_handler вызывает send_basket, обновляя состояние корзины"""
    elif call.data == 'check':
        send_basket(call.message.chat.id)

    elif call.data == 'confirm':
        confirm_order(call.message)

    elif call.data == 'track_time':
        track_time(call.message.chat.id)
        # bot.send_message(call.message.chat.id, "Заказ активен ушел в БД и пошел готовиться")
        # bot.send_message(call.message.chat.id, "Ждем какую-то функцию подтверждения от Мирослава и Влада")
        # bot.send_message(call.message.chat.id,
        #                  "Отложенное сообщение на id клиента через время готовки макс блюда + 30 минут. Реализация?")
        # bot.send_message(call.message.chat.id, "Доставлен ли заказ? Оставьте, пожалуйста, комментарий: ГДЕ?")


print("Ready")

if __name__ == "__main__":
    start_scheduler_thread()


    @bot.message_handler(content_types=['text'])
    def message_handler(message):
        try:
            start(message)
        except Exception as e:
            logging.error(f"Error in message_handler: {e}")


    @bot.callback_query_handler(func=lambda call: True)
    def callback_handler(call):
        try:
            query_handler(call)
        except Exception as e:
            logging.error(f"Error in callback_handler: {e}")


    # while True:
    #     try:
    #         bot.infinity_polling(timeout=10, long_polling_timeout=5)
    #     except Exception as e:
    #         logging.error(f"Infinity polling exception: {e}")
    #         time.sleep(15)

    bot.infinity_polling()
