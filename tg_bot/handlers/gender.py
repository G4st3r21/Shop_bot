from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from handlers.default import default_message
from keys.gender import generate_gender_keyboard
from states import UserFilters


async def cmd_gender(callback_query: CallbackQuery):
    await callback_query.answer()
    gender_types_kb = generate_gender_keyboard()
    await callback_query.message.edit_text("Выберите пол: ", reply_markup=gender_types_kb)
    await UserFilters.choosing_gender.set()


async def gender_chosen(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    if callback_query.data == 'delete':
        await state.update_data(chosen_gender=None)
    elif callback_query.data in ['male', 'female']:
        gender = "мужской" if callback_query.data == 'male' else "женский"
        await state.update_data(chosen_gender=gender)
        await callback_query.message.edit_text(text="Пол выбран")

    await default_message(callback_query, state)


async def gender_error(callback_query: CallbackQuery):
    await callback_query.answer()
    await callback_query.message.answer(
        text="Я такого пола не знаю, попробуйте еще раз"
    )


def register_handlers_gender(dp: Dispatcher):
    dp.register_callback_query_handler(cmd_gender, lambda c: c.data == 'gender')
    dp.register_callback_query_handler(
        gender_chosen,
        state=UserFilters.choosing_gender
    )
    dp.register_callback_query_handler(gender_error, state=UserFilters.choosing_gender)
