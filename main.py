import telebot
from IgorFuntions import is_valid_email
from Peremen import token
from Peremen import user_data

bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start', 'profile', 'menu', 'basket', 'history', 'my_orders'])
def handle_command(message):
    bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
    if message.text == '/start':
        #проверка id через функцию Оли(возвращает true или false)
        #регистрируем пользователя
        regist(message)
    elif message.text == '/profile':
        print(1)


#                                   БЛОК РЕГИСТРАЦИИ                                    #
#########################################################################################
def regist(message):
    bot.send_message(message.chat.id, "Добро пожаловать в бот *****"
                                      "Пожалуйста предоставьте данные для регистрации")
    msg = bot.send_message(message.chat.id, "Как вас зовут:")
    bot.register_next_step_handler(msg, reg_name)


def reg_name(message):
    user_data.update({message.from_user.id: [message.text]})
    msg = bot.send_message(message.chat.id, 'Как мы можем с вами связаться?')
    bot.register_next_step_handler(msg, reg_tp_number)


def reg_tp_number(message):
    if len(message.text) == 13 and message.text[:4] == '+375' and message.text[4:6] in ['29', '33', '44']:
        user_data[message.from_user.id].append(message.text)
        msg = bot.send_message(message.chat.id, 'Какой у вас email?')
        bot.register_next_step_handler(msg, reg_email)
    else:
        msg = bot.send_message(message.chat.id, 'Неверный номер, попробуйте еще раз')
        bot.register_next_step_handler(msg, reg_tp_number)
        #продумать кнопку возврат на шаг назад


#функция для проверки введнного адреса почты
def reg_email(message):
    if is_valid_email(message.text):
        # продумать кнопку возврат на шаг назад
        user_data[message.from_user.id].append(message.text)
        bot.send_message(message.chat.id, 'Спасибо за регистрацию!')
        print(user_data)  #user_data(список из 3 элементов нужно отправить в Бд)
        message.text = '/profile'
    else:
        msg = bot.send_message(message.chat.id, 'Неверный паттерн почты, попробуйте еще раз')
        bot.register_next_step_handler(msg, reg_email)

#########################################################################################

#                                   БЛОК ИЗМЕНЕНИЯ ПРОФИЛЯ                              #
#########################################################################################


def set_profile():
    pass



#########################################################################################
bot.infinity_polling()
