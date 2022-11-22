from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def generate_default_keyboard(show_product=False):
    button_gender = InlineKeyboardButton('Пол', callback_data="gender")
    button_categories = InlineKeyboardButton('Категории', callback_data="categories")
    button_brands = InlineKeyboardButton('Бренды', callback_data="brands")
    button_show_products = InlineKeyboardButton('Показать товары', callback_data="products")

    all_types_kb = InlineKeyboardMarkup()
    all_types_kb.row(button_gender, button_categories, button_brands)
    if show_product:
        all_types_kb.add(button_show_products)

    return all_types_kb
