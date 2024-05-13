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
authorized_users = {}

connection = sqlite3.connect('db.sql')
cursor = connection.cursor()

with open('database.sql', 'r') as sql_file:
    sql_script = sql_file.read()
    cursor.executescript(sql_script)

connection.commit()
connection.close()

def log_event(event_type, user_id=None, username=None, todo_id=None, todo_text=None):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if event_type == 'register':
        with open('logs.txt', 'a') as log_file:
            log_file.write(f"{current_time}: User {username} registered in system\n")
    elif event_type == 'login':
        with open('logs.txt', 'a') as log_file:
            log_file.write(f"{current_time}: User {username} with ID {user_id} logged in system\n")
    elif event_type == 'todo_added':
        with open('logs.txt', 'a') as log_file:
            log_file.write(f"{current_time}: Todo {todo_id} added by {username} with User_ID {user_id}. Text: {todo_text}\n")
    elif event_type == 'todo_removed':
        with open('logs.txt', 'a') as log_file:
            log_file.write(f"{current_time}: Todo {todo_id} removed by {username} with User_ID {user_id}\n")
    elif event_type == 'todos_showed':
        with open('logs.txt', 'a') as log_file:
            log_file.write(f"{current_time}: Todos showed for {username} with User_ID {user_id}\n")

@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.ReplyKeyboardMarkup(True)
    button1 = types.KeyboardButton('Register')
    button2 = types.KeyboardButton('Login')
    keyboard.add(button1, button2)
    bot.send_message(message.chat.id, 'Hey, I am TaskMan4u, Bot for storing your todos. Please choose Register or Login to continue.', reply_markup=keyboard)
    bot.register_next_step_handler(message, register_or_login)

def register_or_login(message):
    choice = message.text.strip().lower()
    if choice == 'register':
        bot.send_message(message.chat.id, 'You chose to Register. Please enter your username and password in the format: Username Password')
        bot.register_next_step_handler(message, register)
    elif choice == 'login':
        bot.send_message(message.chat.id, 'You chose to Login. Please enter your username and password in the format: Username Password')
        bot.register_next_step_handler(message, login)
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

    connection = sqlite3.connect('db.sql')
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
        log_event('register', username=username)
        cursor.execute('SELECT id FROM Users WHERE name=?', (username,))
        user_id = cursor.fetchone()[0]
        authorized_users[message.chat.id] = user_id
        log_event('login', user_id=user_id, username=username)
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

    connection = sqlite3.connect('db.sql')
    cursor = connection.cursor()

    cursor.execute('SELECT id, password FROM Users WHERE name=?', (username,))
    user_data = cursor.fetchone()

    if user_data:
        user_id, correct_password = user_data
        if password == correct_password:
            authorized_users[message.chat.id] = user_id
            bot.send_message(message.chat.id, f'Welcome, {username}! You successfully logged in to your account.')
            log_event('login', user_id=user_id, username=username)
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
    user_id = authorized_users.get(message.chat.id)
    if user_id:
        connection = sqlite3.connect('db.sql')
        cursor = connection.cursor()
        cursor.execute('SELECT name FROM Users WHERE id=?', (user_id,))
        username = cursor.fetchone()[0]
        if username.lower() == 'admin':
            keyboard = types.ReplyKeyboardMarkup(True)
            button1 = types.KeyboardButton('Check logs')
            button2 = types.KeyboardButton('View Users')
            button3 = types.KeyboardButton('View Todos')
            keyboard.add(button1, button2, button3)
            bot.send_message(message.chat.id, 'Admin actions:', reply_markup=keyboard)
        else:
            keyboard = types.ReplyKeyboardMarkup(True)
            button1 = types.KeyboardButton('Add Todo')
            button2 = types.KeyboardButton('Show Todos')
            button3 = types.KeyboardButton('Remove Todo')
            keyboard.add(button1, button2, button3)
            bot.send_message(message.chat.id, 'What would you like to do?', reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, 'You are not logged in. Please login first.')

@bot.message_handler(func=lambda message: message.text == 'Check logs')
def send_logs(message):
    user_id = authorized_users.get(message.chat.id)
    if user_id:
        connection = sqlite3.connect('db.sql')
        cursor = connection.cursor()
        cursor.execute('SELECT name FROM Users WHERE id=?', (user_id,))
        username = cursor.fetchone()[0]
        cursor.close()
        connection.close()

        if username.lower() == 'admin':
            with open('logs.txt', 'rb') as log_file:
                bot.send_document(message.chat.id, log_file, caption='Here are the logs.txt:')
        else:
            bot.send_message(message.chat.id, 'You do not have permission to perform this action.')
    else:
        bot.send_message(message.chat.id, 'You are not logged in. Please login first.')
        
@bot.message_handler(func=lambda message: message.text == 'View Users')
def view_users(message):
    user_id = authorized_users.get(message.chat.id)
    if user_id:
        connection = sqlite3.connect('db.sql')
        cursor = connection.cursor()
        cursor.execute('SELECT name FROM Users WHERE id=?', (user_id,))
        username = cursor.fetchone()[0]
        cursor.close()
        connection.close()

        if username.lower() == 'admin':
            connection = sqlite3.connect('db.sql')
            cursor = connection.cursor()
            cursor.execute('SELECT id, name, password FROM Users')
            users = cursor.fetchall()
            cursor.close()
            connection.close()

            users_text = 'User_ID\tUser_Name\tUser_Password\n'
            for user in users:
                users_text += f'{user[0]}\t{user[1]}\t{user[2]}\n'

            with open('users.txt', 'w') as users_file:
                users_file.write(users_text)

            with open('users.txt', 'rb') as users_file:
                bot.send_document(message.chat.id, users_file, caption='Here are the users:')
        else:
            bot.send_message(message.chat.id, 'You do not have permission to perform this action.')
    else:
        bot.send_message(message.chat.id, 'You are not logged in. Please login first.')


@bot.message_handler(func=lambda message: message.text == 'View Todos')
def view_todos(message):
    user_id = authorized_users.get(message.chat.id)
    if user_id:
        connection = sqlite3.connect('db.sql')
        cursor = connection.cursor()
        cursor.execute('SELECT name FROM Users WHERE id=?', (user_id,))
        username = cursor.fetchone()[0]
        cursor.close()
        connection.close()

        if username.lower() == 'admin':
            connection = sqlite3.connect('db.sql')
            cursor = connection.cursor()
            cursor.execute('SELECT id, user_id, todo_text, todo_date FROM Todos')
            todos = cursor.fetchall()
            cursor.close()
            connection.close()

            todos_text = 'Todos_ID\tUser_ID\tTodos_text\tTodos_date\n'
            for todo in todos:
                todos_text += f'{todo[0]}\t{todo[1]}\t{todo[2]}\t{todo[3]}\n'

            with open('todos.txt', 'w') as todos_file:
                todos_file.write(todos_text)

            with open('todos.txt', 'rb') as todos_file:
                bot.send_document(message.chat.id, todos_file, caption='Here are the todos:')
        else:
            bot.send_message(message.chat.id, 'You do not have permission to perform this action.')
    else:
        bot.send_message(message.chat.id, 'You are not logged in. Please login first.')

@bot.message_handler(func=lambda message: message.text == 'Add Todo')
def add_todo_start(message):
    user_id = authorized_users.get(message.chat.id)
    if user_id:
        bot.send_message(message.chat.id, 'Pick a date for your Todo:', reply_markup=calendar.create_calendar(
            name=callbacks.prefix,
            year=now.year,
            month=now.month
        ))
    else:
        bot.send_message(message.chat.id, 'You are not logged in. Please login first.')

@bot.callback_query_handler(func=lambda call: call.data.startswith(callbacks.prefix))
def callback_inline(call):
    name, action, year, month, day = call.data.split(callbacks.sep)
    date = calendar.calendar_query_handler(bot=bot, call=call, name=name, action=action, year=year, month=month,
                                           day=day)
    if action == 'DAY':
        c_date = date.strftime("%Y-%m-%d")
        msg = bot.send_message(chat_id=call.from_user.id, text='What todo: ')
        bot.register_next_step_handler(msg, lambda message: add_todo_save(message, chat_id=call.from_user.id, c_date=c_date))

def add_todo_save(message, chat_id, c_date):
    todo = message.text
    connection = sqlite3.connect('db.sql')
    cursor = connection.cursor()
    cursor.execute('INSERT INTO Todos (user_id, todo_text, todo_date) VALUES (?, ?, ?)', (authorized_users.get(chat_id), todo, c_date))
    connection.commit()
    cursor.execute('SELECT last_insert_rowid()')
    todo_id = cursor.fetchone()[0]
    cursor.close()
    connection.close()
    bot.send_message(chat_id=chat_id, text=f'Todo successfully added on {c_date}')
    log_event('todo_added', user_id=authorized_users.get(chat_id), username=message.from_user.username, todo_id=todo_id, todo_text=todo)

@bot.message_handler(func=lambda message: message.text == 'Show Todos')
def show_todos(message):
    user_id = authorized_users.get(message.chat.id)
    if user_id:
        connection = sqlite3.connect('db.sql')
        cursor = connection.cursor()
        cursor.execute('SELECT id, todo_text, todo_date FROM Todos WHERE user_id=?', (user_id,))
        todos = cursor.fetchall()
        cursor.close()
        connection.close()
        if todos:
            todo_list = '\n'.join(f'{todo[2]}: "{todo[1]}" (ID: {todo[0]})' for todo in todos)
            bot.send_message(message.chat.id, f'Your Todos:\n{todo_list}')
            log_event('todos_showed', user_id=user_id, username=message.from_user.username)
        else:
            bot.send_message(message.chat.id, 'You have no Todos.')
    else:
        bot.send_message(message.chat.id, 'You are not logged in. Please login first.')

@bot.message_handler(func=lambda message: message.text == 'Remove Todo')
def remove_todo_start(message):
    bot.send_message(message.chat.id, 'Enter the ID of the todo you want to remove:')
    bot.register_next_step_handler(message, remove_todo)

def remove_todo(message):
    todo_id = message.text.strip()
    user_id = authorized_users.get(message.chat.id)
    if user_id:
        connection = sqlite3.connect('db.sql')
        cursor = connection.cursor()
        cursor.execute('DELETE FROM Todos WHERE id=? AND user_id=?', (todo_id, user_id))
        if cursor.rowcount > 0:
            connection.commit()
            bot.send_message(message.chat.id, f'Todo with ID {todo_id} removed successfully.')
            log_event('todo_removed', user_id=user_id, username=message.from_user.username, todo_id=todo_id)
        else:
            bot.send_message(message.chat.id, 'Todo not found or you do not have permission to remove it.')
        cursor.close()
        connection.close()
    else:
        bot.send_message(message.chat.id, 'You are not logged in. Please login first.')

bot.polling(none_stop=True)

