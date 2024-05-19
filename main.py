import MINE
@bot.message_handler(content_types=['text'])
def start(message):
    if message == '/start':
        user_id = message.from_user.id
        if user_id not in [list]:
    elif message == '/profile':

@bot.callback_query_handler(func = lambda call: True)
def func(call):
    pass

def regist(user_id):
    pass
    #сообщения + отдаем список с введенными данными