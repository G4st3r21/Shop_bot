from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from models import Brand


def generate_brand_buttons(brand_list: list[Brand], chosen_brands: list[str]):
    brands_types_kb = InlineKeyboardMarkup(row_width=2)
    brands = [
        InlineKeyboardButton(brand.title+" ✅", callback_data=str(brand.title)) if brand.title in chosen_brands
        else InlineKeyboardButton(brand.title, callback_data=str(brand.title))
        for brand in brand_list
    ]

    brands_types_kb.add(*brands)
    brands_types_kb.row(
        InlineKeyboardButton("Выбрать всё", callback_data="all"),
        InlineKeyboardButton('Сбросить', callback_data='delete'),
        InlineKeyboardButton('Назад', callback_data='menu')
    )

    return brands_types_kb
