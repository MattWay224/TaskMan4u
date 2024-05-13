# TaskMan4u
TaskManager via Telegram Bot. Save your todos and bot will help to remember about them!

Installation guide:
make sure that you using python >= v 3.10

sudo apt update
sudo apt install sqlite3
sudo apt install nginx
sudo apt install docker
pip install telebot telebot_calendar
sudo apt install sqlite3

Then you can download the acrive of the project and run main.py using following command:

python main.py


Development:
Implemented SQLite for database structure simplicity and ease of integration.
Developed the Telegram bot using the Telebot library in Python.
Configured NGINX as a reverse proxy to handle requests routed to the bot.
Containerized the solution using Docker for portability and scalability.
Developed unit tests to validate critical components' functionality.
