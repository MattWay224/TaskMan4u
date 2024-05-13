# TaskMan4u

TaskManager via Telegram Bot. Save your todos and the bot will help to remember them!

## Installation Guide:

Make sure that you are using Python >= 3.10

```bash
sudo apt update
sudo apt install sqlite3
sudo apt install nginx
sudo apt install docker
pip install telebot telebot_calendar
```
# Running the Bot:
1. Download the project archive.
2. Navigate to the project directory.
3. Run main.py using the following command:

```python
python main.py
```

# Development:
1. Implemented SQLite for database structure simplicity and ease of integration.
2. Developed the Telegram bot using the Telebot library in Python.
3. Configured NGINX as a reverse proxy to handle requests routed to the bot.
4. Containerized the solution using Docker for portability and scalability.
5. Developed unit tests to validate critical components' functionality.
