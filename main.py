import MINE
@bot.message_handler(content_types=['text'])
def start(message):
    if message == '\start':
        pass
    elif message == "\dmin":
        pass

@bot.callback_query_handler(func = lambda call: True)
def func(call):
    #
    MINE.func(call)
