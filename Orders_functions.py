import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from My import BotToken
from DBfunctions import db
from Sheduler import schedule_message, start_scheduler_thread
import logging
import time
import threading
from Order import user_order_dict

logging.basicConfig(level=logging.INFO)

bot = telebot.TeleBot(BotToken.token)

markupH = types.InlineKeyboardMarkup()
button_1 = types.InlineKeyboardButton('Help', callback_data='help')
button_2 = types.InlineKeyboardButton('Заказ подтвержден', callback_data='order')
button_3 = types.InlineKeyboardButton('Сколько времени осталось?', callback_data='time')
markupH.add(button_1)
markupH.add(button_2)
markupH.add(button_3)

# my_dict_orders = {"user_tg_chat_id": [(1, 'Пицца', 1, 20), (2, 'Омлет', 1, 17), (3, 'Фо-бо', 1, 33), ]}
"""заполнить чем-то для проверки на наличие текущего заказа"""
# user_order_dict = {message.chat.id: [(1, 'Пицца', 1, 20), (), (), ]}

# Для сохранения время отправки
order_schedule_times = {}
# хрень для сохранения заказа в бд
list_order_for_bd = []

"""Функция получения истории заказов из БД и перевод их в список [номер заказа-дата](вроде?).
На вход принимается история заказов из БД по Ольгиной функции в виде списка кортежей. Что ж за жизнь, то такая?"""


# data_history = db.orders_history(message.chat.id)


def history_orders(data):
    list_history_orders = []

    for index, history in enumerate(data):
        """взять из Оленой функции набор с заказами и вывести их по одному: заказ номер - дата"""
        res_history = f'{history[0]} - {history[3]}'  # Форматирование строки с номером заказа и датой
        list_history_orders.append((res_history, history[0]))  # Возвращаем строку и history[0]
    return list_history_orders


# """Функция для вычисления максимального времени приготовления блюда"""
# # список id блюд из корзины для получения времени готовки. Наверное передать Ольге и у нее получить как-то список?
# # id_dishes_orders = [id_dish[0] for id_dish in my_dict_orders["user_tg_chat_id"]]
# id_dishes_orders = [id_dish[0] for id_dish in user_order_dict[message.chat.id]]
# print(id_dishes_orders)


def get_max_cooking_time(orders):
    max_cooking_time = []

    for id_order in orders:
        dish_data = db.dish_data_on_id(id_order)
        print(dish_data)
        max_cooking_time.append(dish_data[4])
    print(max(max_cooking_time))
    # затем этот список или что-то передать в get_max_cooking_time
    return max(max_cooking_time) if orders else 0


"""инлайн-кнопки, для истории заказов?"""
# data_history = db.orders_history(message.chat.id)
# data_history = db.orders_history('3fdf5g544')  # Тест
"""тест для истории заказов?"""
# data_history = [(1, 1, 1, '20240519 15:40:00', 50, 'г Минск, пр Держинского 154'),
#                 (2, 1, 1, '20240519 16:40:00', 50, 'г Минск, пр Держинского 84'),
#                 (3, 1, 1, '20240519 17:40:00', 50, 'г Минск, пр Держинского 154'),
#                 (4, 1, 1, '20240519 18:40:00', 50, 'г Минск, пр Держинского 15'),
#                 (5, 1, 1, '20240519 19:40:00', 50, 'г Минск, пр Держинского 54'),
#                 (6, 1, 1, '20240519 20:40:00', 50, 'г Минск, пр Держинского 14')]  # Тест
#
# print(history_orders(data_history))

"""Функция `generate_markup(page)` создает клавиатуру с кнопками для навигации по страницам"""


# def generate_markup(page):
def generate_markup(page, data_history):
    markup = InlineKeyboardMarkup(row_width=1)
    start_index = page * 2  # Начальный индекс для отображаемых заказов
    end_index = start_index + 2  # Конечный индекс для отображаемых заказов
    for item, order_id in history_orders(data_history)[start_index:end_index]:
        print(item, order_id)
        markup.add(InlineKeyboardButton(item, callback_data="m" + str(order_id)))
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("<<<", callback_data='<' + str(page - 1)))
    if end_index < len(history_orders(data_history)):
        nav_buttons.append(InlineKeyboardButton(">>>", callback_data='>' + str(page + 1)))
    markup.row(*nav_buttons)
    return markup


"""Функция обработки history"""


def check_history(message):
    data_history = db.orders_history(message.chat.id)  # Получение истории заказов из БД
    if not data_history:
        bot.send_message(message.chat.id, "Истории заказов нет.")
        return
    bot.send_message(
        message.chat.id, "Список завершенных заказов.",
    )
    bot.send_message(
        message.chat.id, "Выберите один из заказов ⬇️:",
        reply_markup=generate_markup(0, data_history)
    )


"""Функция обработки my_orders"""


def check_my_orders(message):
    data_my_order = db.my_orders(message.chat.id)
    if not data_my_order:
        bot.send_message(message.chat.id, "У вас нет текущих заказов.")
        return
    data_my_client = db.get_client_data(message.chat.id)
    # data_dishes_my_order = db.dishes_data(history[0])
    # data_my_order = db.my_orders('nfj4j3nj4')  # Тест
    # data_my_client = db.get_client_data('nfj4j3nj4')  # Тест
    # data_dishes_my_order = db.dishes_data(1)  # Тест
    id_my_order = data_my_order[0][0]  # Да ладно, охренеть
    print(id_my_order)
    data_dishes_my_order = db.dishes_data(id_my_order)  # Тест
    print(data_my_order)
    print(data_my_client)

    """проверка на наличие текущего заказа в БГ"""
    # if my_dict_orders["user_tg_chat_id"]:
    # if user_order_dict[message.chat.id]:
    if data_my_order[0][2] == 1:
        bot.send_message(message.chat.id, "Ваш заказ вроде доставлен. Хз")
        return

    bot.send_message(message.chat.id, "Текущий заказ ⬇️")
    """выводим данные о клиенте?"""
    """взять их из БД? Вывели"""
    """данные клиента по заказу: имя, телефон, почта, адрес"""
    # for user in data_my_client:
    data_user = f'{data_my_client[2]}\n{data_my_client[3]}\n{data_my_client[4]}\n{data_my_client[5]}'
    bot.send_message(message.chat.id, "Данные о клиенте")
    bot.send_message(message.chat.id, data_user)

    print(data_dishes_my_order)
    """выводим список блюд (тоже из бд c 0 в is_delivered по id клаента)?"""
    """взять их из откуда(из БД по def dishes_data(order_id): наверное. Чистое ХУдожество)?"""
    bot.send_message(message.chat.id, "Список блюд и общая сумма заказа:")
    res_sum = 0
    res_dish_hist = ''
    for dish in data_dishes_my_order:
        print(dish)
        # for dish in data_dishes_my_order:
        res_dish_hist += f'{dish[1]}\n'
        res_sum += dish[2] * dish[3]
    bot.send_message(message.chat.id, res_dish_hist)
    bot.send_message(message.chat.id, (str(res_sum) + " руб."), reply_markup=markupH)


def start(message):
    if message.text == '/my_orders':
        check_my_orders(message)

    if message.text == '/history':
        check_history(message)

    if message.text == '/basket':
        send_basket(message.chat.id)

    elif message.text == 'Подтвердить':
        confirm_order(message)

    """функция send_basket, которая отображает корзину и выводит ее содержимое с инлайн-кнопками"""


def send_basket(chat_id):
    # user_order_dict={6142885563:[(2, 'Омлет', 2, 17.0)]}
    # print(user_order_dict)
    if not user_order_dict:
        bot.send_message(chat_id, "Корзина пуста.")
        return
    if user_order_dict[chat_id]:
        # if my_dict_orders["user_tg_chat_id"]:
        markupB = InlineKeyboardMarkup(row_width=2)
        button_1 = InlineKeyboardButton('Изменить', callback_data='change')
        button_2 = InlineKeyboardButton('Продолжить', callback_data='continue')
        markupB.add(button_1, button_2)

        res_sum_bask = 0
        res_dish_bask = ''
        for dish_bask in user_order_dict[chat_id]:
            print(dish_bask)
            # for dish_bask in my_dict_orders["user_tg_chat_id"]:
            res_dish_bask += f'Блюдо {dish_bask[1]}: цена {dish_bask[3]} руб. - {dish_bask[2]} шт. - итого {dish_bask[2] * dish_bask[3]} руб.\n'
            res_sum_bask += dish_bask[2] * dish_bask[3]

        bot.send_message(chat_id,
                         f"Список блюд c ценой и общая сумма заказа в корзине 🥰:\n{res_dish_bask} Всего: {res_sum_bask} руб.",
                         reply_markup=markupB)
    else:
        bot.send_message(chat_id, "Basket пустая!", reply_markup=None)


def confirm_order(message):
    """Функция для вычисления максимального времени приготовления блюда"""
    # список id блюд из корзины для получения времени готовки. Наверное передать Ольге и у нее получить как-то список?
    # id_dishes_orders = [id_dish[0] for id_dish in my_dict_orders["user_tg_chat_id"]]
    id_dishes_orders = [id_dish[0] for id_dish in user_order_dict[message.chat.id]]
    print(id_dishes_orders)
    # max_cooking_time = get_max_cooking_time(user_order_dict[message.chat.id]) ?
    max_cooking_time = get_max_cooking_time(id_dishes_orders)
    print(max_cooking_time)
    # delay = (max_cooking_time + 30) * 60  # добавляем 30 минут к максимальному времени готовки
    # print(delay)
    delay = max_cooking_time + 1 * 60  # Тест добавляем 1 минут к максимальному времени готовки
    schedule_time = time.time() + delay
    print(schedule_time)

    # Сохраняем время отправки
    order_schedule_times[message.chat.id] = schedule_time
    print(order_schedule_times)

    # Добавляем кнопку для отслеживания времени
    markupPb = types.InlineKeyboardMarkup(row_width=1)
    button_1 = types.InlineKeyboardButton('Подтвердить', callback_data='confirm')
    button_2 = types.InlineKeyboardButton('Отследить время', callback_data='track_time')
    # markupPb.add(button_1, button_2)
    markupPb.add(button_2)
    bot.send_message(message.chat.id, "Что вы хотите сделать дальше?", reply_markup=markupPb)

    # Парафин для БД
    for dish_bask in user_order_dict[message.chat.id]:
        # for dish_bask in my_dict_orders["user_tg_chat_id"]:
        res_order_for_bd = [dish_bask[0], dish_bask[2]]
        list_order_for_bd.append(res_order_for_bd)
    print(list_order_for_bd)
    # формирование непонятной хуйни для записи в БД под видом нового заказа. По-моему, дичь:
    # now_order_for_bd = db.new_order(message.chat.id, schedule_time, list_order_for_bd)
    # print(now_order_for_bd)
    time_for_bd = (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(schedule_time)))
    print(message.chat.id, time_for_bd)
    # db.new_order('nfj4j3nj4', str(time_for_bd), list_order_for_bd)


    bot.send_message(message.chat.id, "Заказ активен ушел в БД и пошел готовиться")

    # bot.send_message(message.chat.id, "Ждем какую-то функцию подтверждения от Мирослава и Влада")

    # запись в БД под видом нового заказа. Вроде протестено, да здесь вообще все протестено:
    db.new_order(message.chat.id, time_for_bd, list_order_for_bd)

    # Гребанная очистка корзины. Куда бы ее засунуть поглубже?

    user_order_dict.pop(message.chat.id)
    print(user_order_dict)

    bot.send_message(message.chat.id,
                     "Отложенное сообщение на id клиента будет отправлено через время готовки макс блюда + 30 минут.")
    # bot.send_message(message.chat.id, "Доставлен ли заказ? Оставьте, пожалуйста, комментарий: ГДЕ?")

    # Планируем отправку отложенного сообщения
    schedule_message(bot, message.chat.id, "Ваш заказ готов и отправлен. Спасибо за ожидание!"
                                           "Оставьте, пожалуйста, комментарий: https://www.instagram.com", delay)

    # db.order_is_delivered(db.my_orders(message.chat.id)[0][0])


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
    bot.answer_callback_query(callback_query_id=call.id)
    # print(call.data)
    flag = call.data[0]
    data = call.data[1:]
    if flag == "m":
        order_id = int(data)  # Извлечение order_id из callback_data
        # print(order_id, type(order_id))
        bot.send_message(call.message.chat.id, f"Выбранный из истории заказ ⬇️: {order_id}")

        data_dishes_hist = db.dishes_data(order_id)
        data_my_client_hist = db.get_client_data(call.message.chat.id)
        # data_dishes_hist = db.orders_history(call.message.chat.id)
        # print(data_dishes_hist)

        data_user = f'{data_my_client_hist[2]}\n{data_my_client_hist[3]}\n{data_my_client_hist[4]}\n{data_my_client_hist[5]}'
        bot.send_message(call.message.chat.id, "Данные о клиенте:")
        bot.send_message(call.message.chat.id, data_user)

        bot.send_message(call.message.chat.id, f"Список блюд и общая сумма выбранного заказа ⬇️: {order_id}")
        res_sum = 0
        res_dish_hist = ''
        for dish in data_dishes_hist:
            res_dish_hist += f'{dish[1]}\n'
            res_sum += dish[2] * dish[3]
        bot.send_message(call.message.chat.id, res_dish_hist)
        bot.send_message(call.message.chat.id, f"{str(res_sum)} руб.")
    elif flag == "<" or flag == ">":
        page = int(data)
        data_history = db.orders_history(call.message.chat.id)  # Получение истории заказов из БД
        if not data_history:
            bot.edit_message_text("Истории заказов нет.", call.message.chat.id, call.message.message_id)
            return
        bot.edit_message_text("Выберите один из заказов ⬇️", call.message.chat.id, call.message.message_id,
                              reply_markup=generate_markup(page, data_history))

    elif flag == "<" or flag == ">":
        page = int(data)
        data_history = db.orders_history(call.message.chat.id)  # Получение истории заказов из БД
        if not data_history:
            bot.edit_message_text("Истории заказов нет.", call.message.chat.id, call.message.message_id)
            return
        bot.edit_message_text("Выберите один из заказов ⬇️", call.message.chat.id, call.message.message_id,
                              reply_markup=generate_markup(page, data_history))


    elif flag == "h":
        # Обработка команды Help
        bot.send_message(call.message.chat.id,
                         "Позвонить ответственному лицу или кому-то там по телефону +375296333111."
                         "Позвони мне, позвони!")

    elif flag == "o":
        # Обработка команды Заказ подтвержден
        data_my_order = db.my_orders(call.message.chat.id)
        print(data_my_order)
        data_my_client = db.get_client_data(call.message.chat.id)
        # data_my_order = db.my_orders('nfj4j3nj4')  # Тест

        db.order_is_delivered(db.my_orders(call.message.chat.id)[0][0])

        """проверка на из-деливерид?"""
        if data_my_order[0][2] == 0:
            bot.send_message(call.message.chat.id, "Ваш заказ еще не доставлен.")

        elif data_my_order[0][2] == 1:
            bot.send_message(call.message.chat.id, "Заказ завершен. Оставьте, пожалуйста, комментарий: "
                                                   "https://www.instagram.com")

    elif flag == "t":
        # Обработка команды Сколько времени осталось?
        track_time(call.message.chat.id)
        # bot.send_message(call.message.chat.id,
        #                  "Ждем шедулера? Бесконечность - это не предел...?")
        bot.send_message(call.message.chat.id,
                         "Бесконечность - это не предел...?")

    """кнопки для изменения basket?"""
    if call.data == 'change':
        markupUB = InlineKeyboardMarkup(row_width=4)
        for ind_but, dish_but in enumerate(user_order_dict[call.message.chat.id]):
            # for ind_but, dish_but in enumerate(my_dict_orders["user_tg_chat_id"]):
            res_upd_dish_bask = f'{dish_but[1]} - {dish_but[2]}'
            button_1 = InlineKeyboardButton('🗑', callback_data=f'delete_{dish_but[0]}')
            button_2 = InlineKeyboardButton('-', callback_data=f'decrease_{dish_but[0]}')
            button_3 = InlineKeyboardButton(res_upd_dish_bask, callback_data=f'info_{dish_but[0]}')
            button_4 = InlineKeyboardButton('+', callback_data=f'increase_{dish_but[0]}')
            markupUB.add(button_1, button_2, button_3, button_4)

        # button_check = InlineKeyboardButton('Подтвердить изменения', callback_data='check')
        # markupUB.add(button_check)

        bot.send_message(call.message.chat.id, "Список блюд для изменения заказа в корзине 🥰:", reply_markup=markupUB)

    elif call.data == 'continue':
        """Проверка зарегистрирован ли пользователь"""
        if db.is_registered(call.message.chat.id):
            # if db.is_registered('3fdf5g544'):
            """выводим данные о клиенте?"""
            """взять их из БД? Вывели"""

            data_my_client = db.get_client_data(call.message.chat.id)
            # data_my_client = db.get_client_data('3fdf5g544')
            # data_my_order = db.my_orders('3fdf5g544')
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
            for dish_bask in user_order_dict[call.message.chat.id]:
                # for dish_bask in my_dict_orders["user_tg_chat_id"]:
                res_dish_bask += f'{dish_bask[1]}\n'
                res_sum_bask += dish_bask[2] * dish_bask[3]

            bot.send_message(call.message.chat.id,
                             f"Список блюд и общая сумма заказа:\n{res_dish_bask}{res_sum_bask} руб.",
                             reply_markup=markupPb)

        """функция удаления блюда в корзине"""
    elif call.data.startswith('delete_'):
        dish_id = int(call.data.split('_')[1])
        user_order_dict[call.message.chat.id] = [dish for dish in user_order_dict[call.message.chat.id] if
                                                 dish[0] != dish_id]
        # my_dict_orders["user_tg_chat_id"] = [dish for dish in my_dict_orders["user_tg_chat_id"] if dish[0] != dish_id]
        bot.send_message(call.message.chat.id, "Блюдо удалено из корзины.")
        # print(my_dict_orders["user_tg_chat_id"])
        send_basket(call.message.chat.id)

        """функция уменьшения кол-ва блюд в корзине"""
    elif call.data.startswith('decrease_'):
        dish_id = int(call.data.split('_')[1])
        for i, dish in enumerate(user_order_dict[call.message.chat.id]):
            # for i, dish in enumerate(my_dict_orders["user_tg_chat_id"]):
            if dish[0] == dish_id:
                if dish[2] > 1:
                    dish_list = list(dish)
                    dish_list[2] -= 1
                    user_order_dict[call.message.chat.id][i] = tuple(dish_list)
                    # my_dict_orders["user_tg_chat_id"][i] = tuple(dish_list)
                else:
                    user_order_dict[call.message.chat.id].pop(i)
                    # my_dict_orders["user_tg_chat_id"].pop(i)
                break
        bot.send_message(call.message.chat.id, "Количество блюда уменьшено.")
        send_basket(call.message.chat.id)

        """функция добавления кол-ва блюд в корзине"""
    elif call.data.startswith('increase_'):
        dish_id = int(call.data.split('_')[1])
        for i, dish in enumerate(user_order_dict[call.message.chat.id]):
            # for i, dish in enumerate(my_dict_orders["user_tg_chat_id"]):
            if dish[0] == dish_id:
                dish_list = list(dish)
                dish_list[2] += 1
                user_order_dict[call.message.chat.id][i] = tuple(dish_list)
                # my_dict_orders["user_tg_chat_id"][i] = tuple(dish_list)
                break
        bot.send_message(call.message.chat.id, "Количество блюда увеличено.")
        # print(my_dict_orders["user_tg_chat_id"])
        send_basket(call.message.chat.id)

        """обработчик check в query_handler вызывает send_basket, обновляя состояние корзины"""
    elif call.data == 'check':
        send_basket(call.message.chat.id)

    elif call.data == 'confirm':
        confirm_order(call.message)

    elif call.data == 'track_time':
        track_time(call.message.chat.id)


print("Ready")

if __name__ == "__main__":
    start_scheduler_thread()


    @bot.message_handler(content_types=['text'])
    def message_handler(message):
        # start(message)
        try:
            start(message)
        except Exception as e:
            logging.error(f"Error in message_handler: {e}")


    @bot.callback_query_handler(func=lambda call: True)
    def callback_handler(call):
        # query_handler(call)
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
