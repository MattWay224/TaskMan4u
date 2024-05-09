import telebot
from telebot import types
from telebot_calendar import Calendar, CallbackData, ENGLISH_LANGUAGE
import datetime
import sqlite3

token = '6931798699:AAGYOBt4wn_z-kTbgqUMV2YRb9Y79lPvrso'
bot = telebot.TeleBot(token)

calendar = Calendar(language=ENGLISH_LANGUAGE)
callbacks = CallbackData('callbacks', 'action', 'year', 'month', 'day')
now = datetime.datetime.now()
todos = {}

#log_file = open('file.log')

authorized = False


@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.ReplyKeyboardMarkup(True)
    button1 = types.KeyboardButton('Add Todo')
    button2 = types.KeyboardButton('Show todos')
    button3 = types.KeyboardButton('Help')
    keyboard.add(button1)
    keyboard.add(button2)
    keyboard.add(button3)
    bot.send_message(message.chat.id, 'Hey, I am TaskMan4u, '
                                      'Bot for storing your todos, so you will remember about them'
                     + message.from_user.first_name + '!', reply_markup=keyboard)
    bot.register_next_step_handler(message, create_database)


def create_database(message):
    conn = sqlite3.connect('db.sql')

    conn.cursor().execute('CREATE TABLE IF NOT EXISTS Users (id serial primary key, '
                          'name varchar(50), password varchar(50), id_of_user int unique')
    conn.commit()
    conn.close()

    bot.send_message(message.chat.id, 'Hey! You need to autorize, write your name here')
    bot.register_next_step_handler(message, user_name)


def user_name(message):
    name = message.text.strip()
    bot.send_message(message.char.id, 'Now, print your password')
    password = message.text.strip()
    id = message.chat.id

    connection = sqlite3.connect('db.sql')
    cursor = connection.cursor()

    cursor.execute('INSERT INTO Users (name, password, id_of_user) VALUES '
                   '("%s", "%s")' % (name, password, id))
    connection.commit()
    cursor.close()
    connection.close()

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton)
    return

#todo: provide help info
@bot.message_handler(commands=['help'])
def hepling(message):
    bot.send_message(message.chat.id, '''helpp''')



#todo: add deletion
def delete_task(chat_id, c_date, task):
    pass


@bot.message_handler(content_types=['text'])
def call(message):
    if message.text.lower() == 'add todo':
        bot.send_message(message.chat.id, 'Pick date',
                         reply_markup=calendar.create_calendar(
                             name=callbacks.prefix,
                             year=now.year,
                             month=now.month)
                         )
    elif message.text.lower() == 'show todos':
        #todo:
        bot.send_message(message.chat.id, '''here are you tasks''')
    elif message.text.lower() == 'help':
        bot.send_message(message.chat.id, '''helpp''')
    else:
        bot.send_message(message.chat.id, "I don't understand...")


# todo:
@bot.callback_query_handler(func=lambda call: call.data.startswith('delete:'))
def delete_callback(call):
    #_, date, task = call.data.split(':')
    #delete_task(call.message.chat.id, date, task)
    #bot.answer_callback_query(call.id, text=f'Task "{task}" on {date} deleted')
    pass


#handles calendar
@bot.callback_query_handler(func=lambda call: call.data.startswith(callbacks.prefix))
def callback_inline(call: types.CallbackQuery):
    name, action, year, month, day = call.data.split(callbacks.sep)
    date = calendar.calendar_query_handler(bot=bot, call=call, name=name, action=action, year=year, month=month,
                                           day=day)
    if action == 'DAY':
        c_date = date.strftime("%d.%m.%Y")
        bot.send_message(chat_id=call.from_user.id, text=f'You chose {c_date}')
        msg = bot.send_message(chat_id=call.from_user.id, text='What to plan: ')
        bot.register_next_step_handler(msg, lambda message: add_task(message, chat_id=call.from_user.id, c_date=c_date))
    elif action == 'CANCEL':
        bot.send_message(chat_id=call.from_user.id, text='Cancelled')


# todo:
def add_task(message, chat_id, c_date):
    add_todo(chat_id, c_date, message)
    text = f'Task successfully added on {c_date}'
    bot.send_message(chat_id=chat_id, text=text)


#todo: add to the database
def add_todo(chat_id, c_date, message):
    task = message.text
    if todos.get(chat_id) is not None:
        if todos[chat_id].get(c_date) is not None:
            todos[chat_id][c_date].append(task)
        else:
            todos[chat_id][c_date] = [task]
    else:
        todos[chat_id] = {c_date: [task]}


bot.polling(none_stop=True)
