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

authorized_users = {}

# Create the database and tables
connection = sqlite3.connect('db.sql')
cursor = connection.cursor()

with open('database.sql', 'r') as sql_file:
    sql_script = sql_file.read()
    cursor.executescript(sql_script)

connection.commit()
connection.close()


@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.ReplyKeyboardMarkup(True)
    button1 = types.KeyboardButton('Register')
    button2 = types.KeyboardButton('Login')
    keyboard.add(button1, button2)
    bot.send_message(message.chat.id,
                     'Hey, I am TaskMan4u, Bot for storing your todos. Please choose Register or Login to continue.',
                     reply_markup=keyboard)
    bot.register_next_step_handler(message, register_or_login)


def register_or_login(message):
    choice = message.text.strip().lower()
    if choice == 'register':
        bot.send_message(message.chat.id,
                         'You chose to Register. Please enter your username and password in the format: Username Password')
        bot.register_next_step_handler(message, register)
    elif choice == 'login':
        bot.send_message(message.chat.id,
                         'You chose to Login. Please enter your username and password in the format: Username Password')
        bot.register_next_step_handler(message, login)
    elif choice == 'help':
        keyboard = types.ReplyKeyboardMarkup(True)
        button1 = types.KeyboardButton('Register')
        button2 = types.KeyboardButton('Login')
        keyboard.add(button1, button2)
        bot.send_message(message.chat.id,
                         'Please choose Register or Login to continue.',
                         reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, 'Invalid choice. Please choose Register or Login.')
        bot.register_next_step_handler(message, register_or_login)


def register(message):
    username_password = message.text.strip().split()
    if len(username_password) != 2:
        bot.send_message(message.chat.id, 'Invalid input format. Please enter in the format: Username Password')
        bot.send_message(message.chat.id, 'Invalid register. Please try again.')
        return

    username, password = username_password

    connection = sqlite3.connect('database.sql')
    cursor = connection.cursor()

    cursor.execute('SELECT id FROM Users WHERE name=?', (username,))
    user_exists = cursor.fetchone()

    if user_exists:
        bot.send_message(message.chat.id, 'Username already exists. Please choose a different username.')
        bot.register_next_step_handler(message, register_or_login)
    else:
        cursor.execute('INSERT INTO Users (name, password) VALUES (?, ?)', (username, password))
        connection.commit()
        bot.send_message(message.chat.id, f'Register completed. Welcome, {username}!')
        show_todo_buttons(message)

    cursor.close()
    connection.close()


def login(message):
    username_password = message.text.strip().split()
    if len(username_password) != 2:
        bot.send_message(message.chat.id, 'Invalid input format. Please enter in the format: Username Password')
        bot.send_message(message.chat.id, 'Invalid login. Please try again.')
        return

    username, password = username_password

    connection = sqlite3.connect('database.sql')
    cursor = connection.cursor()

    cursor.execute('SELECT id, password FROM Users WHERE name=?', (username,))
    user_data = cursor.fetchone()

    if user_data:
        user_id, correct_password = user_data
        if password == correct_password:
            authorized_users[message.chat.id] = user_id
            bot.send_message(message.chat.id, f'Welcome, {username}! You successfully logged in to your account.')
            show_todo_buttons(message)
        else:
            bot.send_message(message.chat.id, 'Invalid password.')
            bot.register_next_step_handler(message, register_or_login)
    else:
        bot.send_message(message.chat.id, 'Invalid username. Please register or check your username.')
        bot.register_next_step_handler(message, register_or_login)

    cursor.close()
    connection.close()


def show_todo_buttons(message):
    keyboard = types.ReplyKeyboardMarkup(True)
    button1 = types.KeyboardButton('Add Todo')
    button2 = types.KeyboardButton('Show Todos')
    button3 = types.KeyboardButton('Remove Todo')
    keyboard.add(button1, button2, button3)
    bot.send_message(message.chat.id, 'What would you like to do?', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith(callbacks.prefix))
def callback_inline(call):
    name, action, year, month, day = call.data.split(callbacks.sep)
    date = calendar.calendar_query_handler(bot=bot, call=call, name=name, action=action, year=year, month=month,
                                           day=day)
    if action == 'DAY':
        c_date = date.strftime("%d.%m.%Y")
        msg = bot.send_message(chat_id=call.from_user.id, text='What todo: ')
        bot.register_next_step_handler(msg,
                                       lambda message: add_todo_save(message, chat_id=call.from_user.id, c_date=c_date))
    elif action == 'CANCEL':
        bot.send_message(chat_id=call.from_user.id, text='Cancelled')


def add_todo_save(message, chat_id, c_date):
    todo = message.text
    connection = sqlite3.connect('database.sql')
    cursor = connection.cursor()
    cursor.execute('INSERT INTO Todos (user_id, todo_text) VALUES (?, ?)', (authorized_users.get(chat_id), todo))
    connection.commit()
    cursor.close()
    connection.close()
    bot.send_message(chat_id=chat_id, text=f'Todo succ  essfully added on {c_date}')


@bot.message_handler(content_types=['text'])
def call(message):
    if message.text.lower() == 'add todo':
        bot.send_message(message.chat.id, 'Pick a date for your Todo:', reply_markup=calendar.create_calendar(
            name=callbacks.prefix,
            year=now.year,
            month=now.month
        ))
    elif message.text.lower() == 'show todos':
        if not todos.get(message.chat.id):
            bot.send_message(message.chat.id, 'No tasks')
        else:
            bot.send_message(message.chat.id, '''here are you tasks''')
            connection = sqlite3.connect('database.sql')
            cursor = connection.cursor()
            userid = message.chat.id
            # todo: Will it work?
            cursor.execute('SELECT (user_id, todo_text) FROM Todos WHERE user_id == userid')
            connection.commit()
            cursor.close()
        connection.close()
    elif message.text.lower() == 'help':
        bot.send_message(message.chat.id, '''I need somebody HELP''')
    else:
        bot.send_message(message.chat.id, "I don't understand...")


# todo: add deletion
def delete_task(chat_id, c_date, task):
    #if todos.get(chat_id) is not None:
    #    if todos[chat_id].get(c_date) is not None:
    #        todos[chat_id] = None
    pass


@bot.callback_query_handler(func=lambda call: call.data.startswith('delete:'))
def delete_callback(call):
    #_, date, task = call.data.split(':')
    #delete_task(call.message.chat.id, date, task)
    #bot.answer_callback_query(call.id, text=f'Task "{task}" on {date} deleted')
    pass


bot.polling(none_stop=True)
