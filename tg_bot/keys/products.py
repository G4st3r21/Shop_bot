from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def generate_product_keyboard(link=None, need_menu_button=False, need_more_button=False):
    all_product_kb = InlineKeyboardMarkup()
    if link:
        all_product_kb.add(InlineKeyboardButton(text='Связаться с продавцом', url=link))
    if need_menu_button:
        button_back = InlineKeyboardButton('В меню', callback_data="menu")
        all_product_kb.add(button_back)
    if need_more_button:
        button_next = InlineKeyboardButton('Далее', callback_data="next")
        all_product_kb.add(button_next)

    return all_product_kb
