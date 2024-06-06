import json
import os
import threading
import time

import requests
import telebot

# Ваш токен бота Telegram
TELEGRAM_BOT_TOKEN = "7383205503:AAE1nd1mC4w6ztZCzW_SquD5TOGXZT7DWn4"

# ID чата, в который будут отправляться уведомления
CHAT_ID = "1903751935"

# Пороговое значение цены биткоина (в USD), при достижении которого будет отправлено уведомление
THRESHOLD_PRICE = 50000

file_name = "meta.json"

def get_bitcoin_price():
    try:
        response = requests.get("https://api.coindesk.com/v1/bpi/currentprice.json")
        data = response.json()
        bitcoin_price = float(data["bpi"]["USD"]["rate"].replace(",", ""))
        return bitcoin_price
    except Exception as e:
        print(f"Error fetching Bitcoin price: {e}")
        return None


def calculate_percentage_difference(value1, value2):
    try:
        # Проверка на деление на ноль
        if value1 == 0:
            raise ValueError("Первая сумма не должна быть равна нулю.")

        # Вычисление разницы в процентах
        difference = value2 - value1
        percentage_difference = (difference / value1) * 100

        return abs(percentage_difference)
    except Exception as e:
        return str(e)

def send_notification(bot):
    bitcoin_price = get_bitcoin_price()
    if bitcoin_price is not None:
        with open(file_name, 'r') as f:
            data = json.load(f)
        for coin in data:
            if calculate_percentage_difference(bitcoin_price, float(coin["price"])) < float(coin["percent"]):
                message = f"Цена биткоина достигла {bitcoin_price:.2f} USD! 🚀"
                bot.send_message(CHAT_ID, message)



def handle_document(bot, message):
    try:
        # Получите идентификатор файла и загрузите его
        file_id = message.document.file_id
        file_info = bot.get_file(file_id)
        file_path = file_info.file_path
        downloaded_file = bot.download_file(file_path)

        # Сохраните файл локально
        with open(file_name, 'wb') as f:
            f.write(downloaded_file)

        # Обработайте файл (например, прочитайте содержимое, проанализируйте и т. д.)
        # ...
        # Отправьте ответ пользователю
        bot.reply_to(message, f"Файл {file_name} успешно обработан!")

    except Exception as e:
        bot.reply_to(message, f"Ошибка при обработке файла: {str(e)}")


def echo(bot, message: telebot.types.Message):
    bot.send_message(CHAT_ID, message.text)
    pass


def main():
    bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
    bot.register_message_handler(lambda message: handle_document(bot, message), content_types=['document'])
    bot.register_message_handler(lambda message: echo(bot, message), content_types=['text'])

    # Функция для запуска bot.polling()
    def polling_thread():
        print("pooling is start")
        bot.polling()

    # Функция для запуска цикла уведомлений
    def notification_thread():
        print("notification is start")
        while True:
            time.sleep(180)
            send_notification(bot)

    # Создание и запуск потоков
    polling = threading.Thread(target=polling_thread)
    notifications = threading.Thread(target=notification_thread)

    polling.start()
    notifications.start()

    # Ожидание завершения потоков (хотя они будут работать бесконечно)
    polling.join()
    notifications.join()

if __name__ == "__main__":
    main()
