from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from models import Category


async def generate_category_buttons(category_list: list[Category], chosen_categories, child=False):
    category_types_kb = InlineKeyboardMarkup(row_width=2)
    if child:
        categories = [
            InlineKeyboardButton(category.title + " ✅", callback_data=category.title)
            if category.title in chosen_categories else
            InlineKeyboardButton(category.title, callback_data=category.title)
            for category in category_list
        ]
    else:
        categories = [
            InlineKeyboardButton(category.title + " ✅", callback_data=category.title)
            if category.title in chosen_categories else
            InlineKeyboardButton(category.title, callback_data=category.title)
            for category in category_list if not category.parent
        ]
    category_types_kb.add(*categories)
    category_types_kb.row(
        InlineKeyboardButton("Выбрать всё", callback_data="all"),
        InlineKeyboardButton('Сбросить', callback_data='delete'),
        InlineKeyboardButton('Назад', callback_data='back')
    )

    return category_types_kb
