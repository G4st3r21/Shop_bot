from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def generate_gender_keyboard():
    button_gender_male = InlineKeyboardButton('Мужской', callback_data="male")
    button_gender_female = InlineKeyboardButton('Женский', callback_data="female")

    gender_types_kb = InlineKeyboardMarkup()
    gender_types_kb.row(button_gender_male, button_gender_female)
    gender_types_kb.row(InlineKeyboardButton('Сбросить', callback_data='delete'),
                        InlineKeyboardButton('Назад', callback_data='menu'))

    return gender_types_kb
