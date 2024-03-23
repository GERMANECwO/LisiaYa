import telebot

from database import get_settings, get_character, get_genre, get_user_request, get_processed_response
from gpt import logging
from telebot import types
from gpt import GPT
from telebot.types import Message
import sqlite3

is_tester = 1162184970

TOKEN = "6477608399:AAHOtPmfZUd6JSm9KqzEIKrrLelxttBnHnw"
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=["start"])
def handle_start(message: Message):
    logging.info("Отправка приветственного сообщения")
    user_name = message.from_user.first_name
    bot.send_message(
        message.chat.id,
        f"Запуск произведен успешно! \n"
        f"Приветствую тебя, {user_name}!\n\nНапиши /help чтобы узнать команды")


@bot.message_handler(commands=["помощь", "help"])
def handle_help(message: Message):
    user_name = message.from_user.first_name
    bot.send_message(
        message.chat.id,
        f"{user_name}! Я твой цифровой помощник!\n\n"
        f"/settings - Настройки, желательно чтобы ты сразу настроил их!\n"
        f"/new_story - Напиши чтобы задать вопрос нейросети!\n"
        f"/clear_settings - Сбросить настройки в /settings\n"
        f"/clear_history - Полная очистка истории общения.\n"
        f"Узнать обо мне подробнее можно командой /about")


@bot.message_handler(commands=['about'])
def about_command(message: Message):
    bot.send_message(message.chat.id, "Рад, что ты заинтересован_а! Мое предназначение — не"
                                      " оставлять тебя в одиночестве и всячески подбадривать! А так же быть твоим"
                                      " личным учителем!")


@bot.message_handler(commands=["settings"])
def settings(message):
    db_file = 'sqlite3.db'
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        user_id = message.from_user.id
        # Проверяем, если уже выбраны предмет и уровень сложности
        cursor.execute('SELECT genre, character FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()

        if result and result[0] is not None:
            # Уже существует запись о пользователе, меняем предметы
            markup_question = types.InlineKeyboardMarkup()
            answer1 = types.InlineKeyboardButton('Информация о настройках', callback_data='info')
            answer2 = types.InlineKeyboardButton('-->', callback_data='right')
            close = types.InlineKeyboardButton('Закрыть меню', callback_data='close')
            markup_question.add(answer1, answer2)
            markup_question.add(close)
            bot.send_message(message.chat.id, f"Добро пожаловать в меню настроек, @{message.from_user.username}!\n\n"
                                              f"Выберите пункт настройки:", reply_markup=markup_question)
        else:
            # Если предмет и уровень сложности не выбраны, предложить выбрать
            cursor.execute('INSERT OR REPLACE INTO users (user_id) VALUES (?)', (user_id,))
            conn.commit()
            markup_question = types.InlineKeyboardMarkup()
            answer1 = types.InlineKeyboardButton('Информация о настройках', callback_data='info')
            answer2 = types.InlineKeyboardButton('-->', callback_data='right')
            close = types.InlineKeyboardButton('Закрыть меню', callback_data='close')
            markup_question.add(answer1, answer2)
            markup_question.add(close)
            bot.send_message(message.chat.id, f"Добро пожаловать в меню настроек, @{message.from_user.username}!\n\n"
                                              f"Выберите пункт настройки:", reply_markup=markup_question)
    except sqlite3.Error as e:
        print("Ошибка при работе с SQLite:", e)
    finally:
        conn.close()


@bot.callback_query_handler(func=lambda call: True)
def settings_menu(call):
    db_file = 'sqlite3.db'
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        if call.data == "info":
            user_id = call.from_user.id
            genre, character = get_settings(user_id)
            bot.answer_callback_query(call.id, f"Информация о настройках\n\nСейчас выбрана настройка\n"
                                               f"\nЖанр {genre}\nПерсонаж {character}")
        elif call.data == "right":
            markup = types.InlineKeyboardMarkup()
            answer1 = types.InlineKeyboardButton('<--', callback_data='left2')
            set1 = types.InlineKeyboardButton('RPG', callback_data='RPG')
            set2 = types.InlineKeyboardButton('современность', callback_data='MOD')
            set3 = types.InlineKeyboardButton('экшен', callback_data='action')
            answer2 = types.InlineKeyboardButton('-->', callback_data='right2')
            close = types.InlineKeyboardButton('Закрыть меню', callback_data='close')
            markup.add(answer1, answer2)
            markup.add(set1, set2, set3)
            markup.add(close)
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          reply_markup=markup)
        elif call.data == 'RPG':
            user_id = call.from_user.id
            genre = 'RPG'
            bot.answer_callback_query(call.id, f"выбран жанр - РПГ!")
            cursor.execute('UPDATE users SET genre = ? WHERE user_id = ?', (genre, user_id))
            conn.commit()
        elif call.data == 'MOD':
            user_id = call.from_user.id
            genre = 'MOD'
            cursor.execute('UPDATE users SET genre = ? WHERE user_id = ?', (genre, user_id))
            conn.commit()
            bot.answer_callback_query(call.id, f"выбран жанр - современность!")
        elif call.data == 'action':
            user_id = call.from_user.id
            genre = 'action'
            cursor.execute('UPDATE users SET genre = ? WHERE user_id = ?', (genre, user_id))
            conn.commit()
            bot.answer_callback_query(call.id, f"выбран жанр - экшен!")

        elif call.data == "left2":
            markup_question = types.InlineKeyboardMarkup()
            answer1 = types.InlineKeyboardButton('Информация о настройках', callback_data='info')
            answer2 = types.InlineKeyboardButton('-->', callback_data='right')
            close = types.InlineKeyboardButton('Закрыть меню', callback_data='close')
            markup_question.add(answer1, answer2)
            markup_question.add(close)
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          reply_markup=markup_question)
        elif call.data == 'right2':
            markup = types.InlineKeyboardMarkup()
            answer1 = types.InlineKeyboardButton('<--', callback_data='right')
            set1 = types.InlineKeyboardButton('обычный работяга', callback_data='human')
            set2 = types.InlineKeyboardButton('авантюрист', callback_data='adventurer')
            set3 = types.InlineKeyboardButton('торговец', callback_data='trader')
            set4 = types.InlineKeyboardButton('учёный', callback_data='scientist')
            close = types.InlineKeyboardButton('Закрыть меню', callback_data='close')
            markup.add(answer1)
            markup.add(set1, set2)
            markup.add(set3, set4)
            markup.add(close)
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          reply_markup=markup)
        elif call.data == 'human':
            user_id = call.from_user.id
            character = 'человек'
            cursor.execute('UPDATE users SET character = ? WHERE user_id = ?',
                           (character, user_id))
            conn.commit()
            bot.answer_callback_query(call.id, f"выбран персонаж - обычный!")
        elif call.data == 'adventurer':
            user_id = call.from_user.id
            character = 'авантюрист'
            cursor.execute('UPDATE users SET character = ? WHERE user_id = ?',
                           (character, user_id))
            conn.commit()
            bot.answer_callback_query(call.id, f"выбран персонаж - авантюрист!")
        elif call.data == 'trader':
            user_id = call.from_user.id
            character = 'торговец'
            cursor.execute('UPDATE users SET character = ? WHERE user_id = ?',
                           (character, user_id))
            conn.commit()
            bot.answer_callback_query(call.id, f"выбран персонаж - торговец!")
        elif call.data == 'scientist':
            user_id = call.from_user.id
            character = 'учёный'
            cursor.execute('UPDATE users SET character = ? WHERE user_id = ?',
                           (character, user_id))
            conn.commit()
            bot.answer_callback_query(call.id, f"выбран персонаж - учёный!")
        elif call.data == "close":
            bot.delete_message(call.message.chat.id, call.message.message_id)
    except sqlite3.Error as e:
        print("Ошибка при работе с SQLite:", e)
    finally:
        conn.close()


@bot.message_handler(commands=['full_story'])
def full_story(message: Message):
    user_id = message.from_user.id
    processed_response = get_processed_response(user_id)

    if processed_response:
        system_content_genre = get_genre(user_id)
        system_content_character = get_character(user_id)
        full_story = (f"Жанр истории: {system_content_genre}\nПерсонаж истории: {system_content_character}\n\nИстория:"
                      f"\n{processed_response}")
        full_story_with_ending = f"{full_story}"
        bot.send_message(chat_id=user_id, text=full_story_with_ending)
    else:
        bot.send_message(chat_id=user_id,
                         text="История еще не завершена. Пожалуйста, запросите завершение истории сначала.")

@bot.message_handler(commands=["clear_settings"])
def clear_database(message):
    user_id = message.from_user.id
    db_file = 'sqlite3.db'
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET genre = NULL, character = NULL WHERE user_id = ?',
                       (user_id,))
        conn.commit()
        bot.send_message(message.chat.id, "Настройки предмета и сложности успешно очищены!")
    except sqlite3.Error as e:
        print("Ошибка при работе с SQLite:", e)
    finally:
        conn.close()


@bot.message_handler(commands=["clear_history"])
def clear_database(message):
    user_id = message.from_user.id
    db_file = 'sqlite3.db'
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET user_request = NULL, processed_response = NULL WHERE user_id = ?',
                       (user_id,))
        conn.commit()
        bot.send_message(message.chat.id, "История успешно очищена!")
    except sqlite3.Error as e:
        print("Ошибка при работе с SQLite:", e)
    finally:
        conn.close()

# для дебаггинга команды
@bot.message_handler(commands=['debug'])
def send_logs(message):
    global is_tester
    if message.from_user.id == is_tester:
        with open("log_file.txt", "rb") as f:
            bot.send_document(message.from_user.id, f)
    else:
        bot.send_message(message.chat.id, "Вы не имеете доступа к данным настройкам!")


@bot.message_handler(commands=["clear_db"])
def clear_database(message):
    global is_tester
    if message.from_user.id == is_tester:
        db_file = 'sqlite3.db'
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM users')  # Очищаем таблицу users
            conn.commit()
            bot.send_message(message.chat.id, "База данных успешно очищена!")
        except sqlite3.Error as e:
            print("Ошибка при работе с SQLite:", e)
        finally:
            conn.close()
    else:
        bot.send_message(message.chat.id, "Вы не имеете доступа к данным настройкам!")


check_story = False


@bot.message_handler(commands=['new_story'])
def new_story(message: Message):
    global check_story
    check_story = True
    bot.reply_to(message, text="Следующим сообщением напиши начало истории.")
    # регистрируем следующий "шаг"
    bot.register_next_step_handler(message, story)


# Обработка промта и отправка результата
@bot.message_handler(func=lambda message: True)
def story(message: Message):
    if check_story:
        if message.text.lower() == "продолжи":
            continue_story(message)
        elif message.text.lower() == "конец":
            end_story(message)
        else:
            continue_previous_response(message)


def continue_story(message: Message):
    user_id = message.from_user.id
    system_content_genre = get_genre(user_id)
    system_content_character = get_character(user_id)
    processed_response = get_processed_response(user_id)
    gpt = GPT(system_content=f"Жанр:{system_content_genre}, персонаж:{system_content_character}",
              processed_response=processed_response)
    response_message = bot.reply_to(message, text="Промт принят! Обрабатываю запрос…")
    user_request = 'Продолжи'
    request = gpt.make_prompt(user_request, processed_response)
    response = gpt.send_request(request)
    processed_response = gpt.process_resp(request, response)

    if response.status_code == 200 and processed_response != "error":
        logging.info("Ответ отправлен успешно.")
        bot.edit_message_text(text=processed_response,
                              chat_id=response_message.chat.id,
                              message_id=response_message.message_id)
        try:
            conn = sqlite3.connect('sqlite3.db')
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET user_request = ?, processed_response = ? WHERE user_id = ?',
                           (request, processed_response, user_id))
            conn.commit()
        except sqlite3.Error as e:
            print("Ошибка при работе с SQLite:", e)
        finally:
            conn.close()
    else:
        error_message = f"Ошибка: {processed_response}" if processed_response == "error" else \
            f"Не удалось отправить ответ от нейросети, код состояния {response.status_code}"
        logging.error(error_message)
        bot.send_message(text=error_message, chat_id=response_message.chat.id)


def end_story(message: Message):
    user_id = message.from_user.id
    global check_story
    check_story = False
    system_content_genre = get_genre(user_id)
    system_content_character = get_character(user_id)
    processed_response = get_processed_response(user_id)

    gpt = GPT(system_content=f"Жанр:{system_content_genre}, персонаж:{system_content_character}",
              processed_response=processed_response)

    response_message = bot.reply_to(message, text="Промт принят! Обрабатываю запрос…")
    user_request = 'Заверши историю.'
    request = gpt.make_prompt(user_request, processed_response)
    response = gpt.send_request(request)
    processed_response = gpt.process_resp(request, response)

    if response.status_code == 200 and processed_response != "error":
        logging.info("Ответ отправлен успешно.")
        bot.edit_message_text(text=f'{processed_response}\n\nЕсли хотите увидеть всю историю, напишите /full_story',
                              chat_id=response_message.chat.id,
                              message_id=response_message.message_id)
        try:
            conn = sqlite3.connect('sqlite3.db')
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET user_request = ?, processed_response = ? WHERE user_id = ?',
                           (user_request, processed_response, user_id))
            conn.commit()
        except sqlite3.Error as e:
            print("Ошибка при работе с SQLite:", e)
        finally:
            conn.close()
    else:
        error_message = f"Ошибка: {processed_response}" if processed_response == "error" else \
            f"Не удалось отправить ответ от нейросети, код состояния {response.status_code}"
        logging.error(error_message)
        bot.send_message(text=error_message, chat_id=response_message.chat.id)


def continue_previous_response(message: Message):
    user_id = message.from_user.id
    system_content_genre = get_genre(user_id)
    system_content_character = get_character(user_id)
    processed_response = get_processed_response(user_id)
    logging.info(f"Полученный текст от пользователя: {message.text}")
    user_request = f'{get_user_request(user_id)} {message.text}'
    gpt = GPT(system_content=f"Жанр:{system_content_genre}, персонаж:{system_content_character}",
              processed_response=processed_response)
    response_message = bot.reply_to(message, text="Промт принят! Обрабатываю запрос…")
    request = gpt.make_prompt(user_request, processed_response)
    response = gpt.send_request(request)
    processed_response = gpt.process_resp(request, response)

    if response.status_code == 200 and processed_response != "error":
        logging.info("Ответ отправлен успешно.")
        bot.edit_message_text(text=processed_response,
                              chat_id=response_message.chat.id,
                              message_id=response_message.message_id)
        try:
            conn = sqlite3.connect('sqlite3.db')
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET user_request = ?, processed_response = ? WHERE user_id = ?',
                           (user_request, processed_response, user_id))
            conn.commit()
        except sqlite3.Error as e:
            print("Ошибка при работе с SQLite:", e)
        finally:
            conn.close()
    else:
        error_message = f"Ошибка: {processed_response}" if processed_response == "error" else \
            f"Не удалось отправить ответ от нейросети, код состояния {response.status_code}"
        logging.error(error_message)
        bot.send_message(text=error_message, chat_id=response_message.chat.id)


if __name__ == "__main__":
    logging.info("Бот запущен")
bot.polling()
