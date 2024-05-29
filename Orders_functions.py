import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from My import Bot_Food_Token
from DBfunctions import db
from FedorFunctions import *

bot = telebot.TeleBot(Bot_Food_Token.TOKEN)

"""кнопки для перебора заказов постранично"""
markupR = types.ReplyKeyboardMarkup(resize_keyboard=True)
button_1 = types.KeyboardButton("<<<")
button_2 = types.KeyboardButton(">>>")
markupR.add(button_1, button_2)

"""кнопки Help, заказ подтвержден, сколько времени осталось?"""
markupH = types.ReplyKeyboardMarkup(resize_keyboard=True)
button_1 = types.KeyboardButton('Help')
button_2 = types.KeyboardButton('Заказ подтвержден')
button_3 = types.KeyboardButton('Сколько времени осталось?')
markupH.add(button_1)
markupH.add(button_2)
markupH.add(button_3)

"""инлайн-кнопки, для истории заказов?"""
markupI = InlineKeyboardMarkup(row_width=1)
data_history = db.orders_history('3fdf5g544')  # Тест
print(data_history)
for index, history in enumerate(data_history):
    """взять из Оленой функции набор с заказами и вывести их по одному: заказ номер - дата"""
    res_hystory = f'{history[0]} - {history[3]}'
    markupI.add(InlineKeyboardButton(res_hystory, callback_data="m" + str(index)))

"""кнопки для basket?"""
markupB = types.ReplyKeyboardMarkup(resize_keyboard=True)
button_1 = types.KeyboardButton('Изменить')
button_2 = types.KeyboardButton('Продолжить')
markupB.add(button_1)
markupB.add(button_2)

# """кнопки для изменения basket?"""
# markupUB = types.ReplyKeyboardMarkup(resize_keyboard=True)
# button_1 = types.KeyboardButton('🗑')
# button_2 = types.KeyboardButton('-')
# button_3 = types.KeyboardButton('Блюдо')
# button_4 = types.KeyboardButton('+')
# markupUB.add(button_1, button_2, button_3, button_4)

"""кнопка для подтверждения basket?"""
markupPb = types.ReplyKeyboardMarkup(resize_keyboard=True)
button_1 = types.KeyboardButton('Подтвердить')
markupPb.add(button_1)

my_dict_orders = {"user_tg_chat_id": [(1, 'Пицца', 1, 20), (2, 'Омлет', 1, 17), (3, 'Фо-бо', 1, 33), ]}
"""заполнить чем-то для проверки на наличие текущего заказа"""


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
        bot.send_message(message.chat.id, data_user, reply_markup=markupH)

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
        bot.send_message(message.chat.id, (str(res_sum) + " руб."))

    elif message.text == 'Help':
        bot.send_message(message.chat.id, "Позвонить ответственному лицу или кому-то там по телефону +375296333111")

    elif message.text == 'Заказ подтвержден':
        # data_my_order = db.my_orders(message.chat.id)
        # data_my_client = db.get_client_data(message.chat.id)
        data_my_order = db.my_orders('nfj4j3nj4')  # Тест
        data_my_client = db.get_client_data('nfj4j3nj4')  # Тест
        """проверка на из-деливерид?"""
        if data_my_order[0][2] == 0:
            bot.send_message(message.chat.id, "Доставлен ли заказ? Оставьте, пожалуйста, комментарий: ГДЕ?")

        elif data_my_order[0][2] == 1:
            bot.send_message(message.chat.id, "Заказ завершен")

    elif message.text == 'Сколько времени осталось?':
        bot.send_message(message.chat.id, "Ждем шедулера? Бесконечность - это не предел...?")

    if message.text == '/history':
        # if not my_dict_orders["user_tg_chat_id"]:
        bot.send_message(
            message.chat.id, "Список завершенных заказов",
            reply_markup=markupR
        )
        bot.send_message(
            message.chat.id, "Выберите один из заказов ⬇️",
            reply_markup=markupI
        )
    #
    # elif message.text == '<<<':
    #

    # x = ['a', 'b', 'c', 'd', 'e', 'w', 'df', 'ww', 'x', 'qa', 'wsx']
    #
    # for i in range(0, len(x), 3):
    #     input('Введи "go" ')
    #     print(x[i: i + 3])
    # print('Выход из цикла')

    if message.text == '/basket':
        # user_dict[message.chat.id] += message.text
        if my_dict_orders["user_tg_chat_id"]:
            bot.send_message(
                message.chat.id, "Список блюд c ценой и общая сумма заказа в корзине 🥰:",
                reply_markup=markupB
            )
            """функция вывода списка блюд c ценой и общей суммой заказа в корзине"""

            # list_dishes_price_basket(my_dict_orders["user_tg_chat_id"])
            res_sum_bask = 0
            # res_dish_bask = ''
            for dish_bask in my_dict_orders["user_tg_chat_id"]:
                print(dish_bask)
                res_dish_bask = f'Блюдо {dish_bask[1]} {dish_bask[3]} - {dish_bask[2]} - {dish_bask[2] * dish_bask[3]}'
                res_sum_bask += dish_bask[2] * dish_bask[3]
                bot.send_message(message.chat.id, res_dish_bask)
            bot.send_message(message.chat.id, (str(res_sum_bask) + " руб."))

        else:
            bot.send_message(message.chat.id, "Basket пустая!", reply_markup=None)

    elif message.text == 'Изменить':

        markupUB = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
        """кнопки для изменения basket?"""
        for ind_but, dish_but in enumerate(my_dict_orders["user_tg_chat_id"]):
            print(dish_but)
            res_upd_dish_bask = f'{dish_but[1]} - {dish_but[2]}'

            button_1 = types.KeyboardButton('🗑')
            button_2 = types.KeyboardButton('-')
            button_3 = types.KeyboardButton(res_upd_dish_bask)
            button_4 = types.KeyboardButton('+')
            markupUB.add(button_1, button_2, button_3, button_4)

        bot.send_message(
            message.chat.id, "Список блюд для изменения заказа в корзине 🥰:",
            reply_markup=markupUB
        )

        """функция вывода списка блюд c ценой и общей суммой заказа в корзине"""
        res_sum_bask = 0
        # res_dish_bask = ''
        for dish_bask in my_dict_orders["user_tg_chat_id"]:
            print(dish_bask)
            res_dish_bask = f'Блюдо {dish_bask[1]} {dish_bask[3]} - {dish_bask[2]} - {dish_bask[2] * dish_bask[3]}'
            res_sum_bask += dish_bask[2] * dish_bask[3]
            bot.send_message(message.chat.id, res_dish_bask)
        bot.send_message(message.chat.id, (str(res_sum_bask) + " руб."))

        """выведение реализации кнопок в разделе изменения заказа"""
    # elif message.text == '🗑':

    elif message.text == 'Продолжить':

        bot.send_message(message.chat.id, "Неизвестный пока /profile 🥰")
        """Проверка зарегистрирован ли пользователь"""
        # if db.is_registered(message.chat.id):
        if db.is_registered('3fdf5g544'):
            """выводим данные о клиенте?"""
            """взять их из БД? Вывели"""

            # data_my_client = db.get_client_data(message.chat.id)
            data_my_order = db.my_orders('3fdf5g544')  # Тест
            data_my_client = db.get_client_data('3fdf5g544')  # Тест
            data_dishes_my_order = db.dishes_data(1)  # Тест

            """данные клиента по заказу: имя, телефон, почта, адрес"""
            """Выводим кнопки"""
            # for user in data_my_client:
            data_user = f'{data_my_client[2]}\n{data_my_client[3]}\n{data_my_client[4]}\n{data_my_client[5]}'
            bot.send_message(message.chat.id, "Данные о клиенте")
            bot.send_message(message.chat.id, data_user, reply_markup=markupPb)

            print(data_my_client)
            print(data_dishes_my_order)
            """выводим список блюд (из корзины)?"""
            """взять их из откуда(basket)?"""
            bot.send_message(message.chat.id, "Список блюд и общая сумма заказа:")

            res_sum_bask = 0
            res_dish_bask = ''
            for dish_bask in my_dict_orders["user_tg_chat_id"]:
                print(dish_bask)
                # res_dish_bask = f'{dish_bask[1]}'
                res_dish_bask += f'{dish_bask[1]}\n'
                res_sum_bask += dish_bask[2] * dish_bask[3]
                # bot.send_message(message.chat.id, res_dish_bask)
            bot.send_message(message.chat.id, res_dish_bask)
            bot.send_message(message.chat.id, (str(res_sum_bask) + " руб."))

    elif message.text == 'Подтвердить':

        bot.send_message(message.chat.id, "Заказ активен ушел в БД и пошел готовиться")
        """Далее должна быть какая-то функция подтверждения от Мирослава и Влада"""
        bot.send_message(message.chat.id, "Ждем какую-то функцию подтверждения от Мирослава и Влада")

        """Нужна какая-то реализация отложенного сообщения"""
        bot.send_message(message.chat.id,
                         "Отложенное сообщение на id клиента через время готовки макс блюда + 30 минут. Реализация?")

        bot.send_message(message.chat.id, "Доставлен ли заказ? Оставьте, пожалуйста, комментарий: ГДЕ?")

def query_handler(call):
    bot.answer_callback_query(callback_query_id=call.id, )
    id = call.message.chat.id
    flag = call.data[0]
    data = call.data[1:]
    if flag == "m":
        # for cat in dict_cat[data]:
        #     markupSh.add(InlineKeyboardButton(cat, callback_data="s" + cat))
        # bot.send_message(call.message.chat.id, "Выбирайте 🥰", reply_markup=markupSh)
        # bot.send_message(call.message.chat.id, data, reply_markup=markupSh)
        bot.send_message(call.message.chat.id, "Текущий заказ ⬇️")
        """выводим данные о клиенте?"""
        """взять их из БД? Вывели"""
        # data_my_order_hist = db.my_orders(message.chat.id)
        # data_my_client_hist = db.get_client_data(message.chat.id)
        # data_dishes_hist = db.dishes_data(history[0])
        data_my_order_hist = db.orders_history('3fdf5g544')  # Тест
        data_my_client_hist = db.get_client_data('3fdf5g544')  # Тест
        data_dishes_hist = db.dishes_data(1)  # Тест

        """данные клиента по заказу: имя, телефон, почта, адрес"""
        # for user in data_my_client:
        data_user = f'{data_my_client_hist[2]}\n{data_my_client_hist[3]}\n{data_my_client_hist[4]}\n{data_my_client_hist[5]}'
        bot.send_message(call.message.chat.id, "Данные о клиенте:")
        bot.send_message(call.message.chat.id, data_user)
        # bot.send_message(call.message.chat.id, data_user, reply_markup=markupH)

        print(data_my_order_hist)
        print(data_my_client_hist)
        print(data_dishes_hist)
        """выводим список блюд (тоже из бд или из корзины)?"""
        """взять их из откуда(БД)?"""
        """НЕ Выводим кнопки"""
        bot.send_message(call.message.chat.id, "Список блюд и общая сумма заказа:")
        res_sum = 0
        res_dish_hist = ''
        for dish in data_dishes_hist:
            res_dish_hist += f'{dish[1]}\n'
            res_sum += dish[2] * dish[3]
        bot.send_message(call.message.chat.id, res_dish_hist)
        bot.send_message(call.message.chat.id, (str(res_sum) + " руб."))

    # if flag == "s":
    #     markupC = InlineKeyboardMarkup()
    #     for ind, shop in dict_shop[data]:
    #         markupC.add(InlineKeyboardButton(shop, callback_data="x" + str(ind)))
    #     bot.send_message(call.message.chat.id, "Выбирайте 🥰", reply_markup=markupC)
    # #     bot.send_message(call.message.chat.id, data, reply_markup=markupC)
    #
    # if flag == "x":
    #     bot.send_message(call.message.chat.id, "Чтобы воспользоваться акцией необходимо: перейти по ссылке, "
    #                                            "скопировать промокод и ввести его на сайте или приложении магазина",
    #                      )
    #     bot.send_message(call.message.chat.id, index_text[data])


print("Ready")


if __name__ == "__main__":
    @bot.message_handler(content_types=['text'])
    def f(message):
        start(message)


    @bot.callback_query_handler(func=lambda call: True)
    def callback_handler(call):
        query_handler(call)

    bot.infinity_polling()
