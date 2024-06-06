import schedule
import time
import threading
from telebot import TeleBot


def send_delayed_message(bot, chat_id, text):
    bot.send_message(chat_id, text)


def schedule_message(bot, chat_id, text, delay):
    schedule_time = time.time() + delay
    schedule.every().day.at(time.strftime('%H:%M:%S', time.localtime(schedule_time))).do(send_delayed_message, bot,
                                                                                         chat_id, text)
    print(f"Сообщение, запланированное для {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(schedule_time))}")


def start_scheduler_thread():
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(1)

    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    print("Запущен поток планировщика")


# @bot.message_handler(commands=['start'])
# def start():
#     bot.send_message(bot.message.chat.id, 'Привет')
#
#
# def schedule_checker():
#     while True:
#         schedule.run_pending()
#         sleep(60)
#
#
# if __name__ == '__main__':
#     schedule.every().day.at('08:30').do(start)
#     Thread(target=schedule_checker).start()
#     bot.polling(none_stop=True, interval=0)
