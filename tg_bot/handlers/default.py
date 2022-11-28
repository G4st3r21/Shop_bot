from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from keys.default import generate_default_keyboard


async def default_message(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await state.reset_state(with_data=False)
    user_data = await state.get_data()
    await state.update_data(offset=0)
    await state.update_data(full_count=0)
    await state.update_data(parent_category=None)
    chosen_gender = user_data['chosen_gender'] if user_data.get('chosen_gender') else "не выбрано"
    chosen_category = ', '.join(user_data['chosen_categories']) if user_data.get('chosen_categories') else "не выбраны"
    chosen_brands = ', '.join(user_data['chosen_brands']) if user_data.get('chosen_brands') else "не выбраны"

    all_types_kb = generate_default_keyboard()
    await callback_query.message.edit_text(
        f"Вами были выбраны следующие фильтры:\n"
        f"-Пол: {chosen_gender}\n"
        f"-Категория: {chosen_category}\n"
        f"-Бренды: {chosen_brands}\n\n"
        "При выбранном бренде доступна кнопка 'Показать предложения'\n\n",
        reply_markup=all_types_kb
    )


async def welcome_message(message: Message):
    all_types_kb = generate_default_keyboard()
    await message.answer(
        "Здравствуйте!\nЯ бот помогающий с покупкой одежды!\n"
        "Пожалуйста выберите следующие фильтры товаров.\n(в дальнейшем их можно будет редактировать)",
        reply_markup=all_types_kb
    )


def register_handlers_default(dp: Dispatcher):
    dp.register_callback_query_handler(default_message, lambda c: c.data == 'back', state=['*'])
    dp.register_message_handler(welcome_message, commands=['start', 'help'])
