import unittest
from unittest.mock import MagicMock
from unittest.mock import AsyncMock
from main import (
    start,
    register_or_login,
    register,
    login,
    show_todo_buttons,
    add_todo_save,
)


class TestTelegramBot(unittest.TestCase):
    def setUp(self):
        self.bot = MagicMock()

    def test_register(self):
        message = MagicMock()
        message.text = 'register'
        register_or_login(message)
        self.bot.send_message.assert_called_with(message.chat.id,
                                                 'You chose to Register. '
                                                 'Please enter your username and password in the format: '
                                                 'Username Password')
        self.bot.register_next_step_handler.assert_called_with(message, register)

    def test_register_username(self):
        message = MagicMock()
        message.text = 'test unittest incorrect'
        register(message)
        self.bot.send_message.assert_called_with(message.chat.id, 'Invalid input format. '
                                                                  'Please enter in the format: '
                                                                  'Username Password')
        self.bot.send_message.assert_called_with(message.chat.id, 'Invalid register. Please try again.')

        message.text = 'admin incorrect'
        register(message)
        self.bot.send_message.assert_called_with(message.chat.id, 'You have no rights to register new admin')
        self.bot.send_message.assert_called_with(message.chat.id, 'Invalid register. Please try again.')

        message.text = 'test correct'
        register(message)
        self.bot.send_message.assert_called_with(message.chat.id, f'Register completed. Welcome, '
                                                                  f'{message.text.split(" ")[0]}!')

    def test_login(self):
        message = MagicMock()
        message.text = 'login'
        register_or_login(message)
        self.bot.send_message.assert_called_with(message.chat.id,
                                                 'You chose to Login. '
                                                 'Please enter your username and password in the format: '
                                                 'Username Password')
        self.bot.register_next_step_handler.assert_called_with(message, login)

    def test_show_todo_buttons(self):
        message = MagicMock()
        message.chat.id = 123
        show_todo_buttons(message)
        expected_buttons = [
            'Add Todo',
            'Show Todos',
            'Remove Todo'
        ]
        self.bot.send_message.assert_called_with(123, 'What would you like to do?',
                                                 reply_markup=MagicMock().add.assert_called_with(expected_buttons))

    def test_add_todo_save(self):
        message = MagicMock()
        message.text = 'Test todo'
        message.chat.id = 123
        c_date = '31.12.2024'
        add_todo_save(message, 123, c_date)
        self.bot.send_message.assert_called_with(123, "Todo successfully added on 01.01.2024")


if __name__ == '__main__':
    unittest.main()
