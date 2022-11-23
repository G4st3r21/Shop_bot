from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from handlers.default import default_message
from db_session import session_db
from keys.brands import generate_brand_buttons
from models import Brand
from states import UserFilters


@session_db
async def cmd_brands(callback_query: CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback_query.answer()
    brand_list = await Brand.get_all(session)

    user_data = await state.get_data()
    chosen_brands = ', '.join(user_data['chosen_brands']) if 'chosen_brands' in user_data.keys() else "не выбраны"

    brands_types_kb = generate_brand_buttons(brand_list, user_data.get('chosen_brands', []))

    await callback_query.message.edit_text(
        f"Выбранные бренды: {chosen_brands}\n"
        "Выберите бренды ниже",
        reply_markup=brands_types_kb
    )
    await UserFilters.choosing_brand.set()


async def brand_chosen(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    brand = callback_query.data
    if brand != 'back':
        chosen_brands = user_data['chosen_brands'] if 'chosen_brands' in user_data.keys() else []
        if brand in chosen_brands:
            chosen_brands.remove(brand)
        else:
            chosen_brands.append(brand)
        await state.update_data(chosen_brands=chosen_brands)
        await cmd_brands(callback_query, state)
    else:
        await default_message(callback_query, state)


async def brand_error(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer(
        text="Я такого бренда не знаю, попробуйте еще раз"
    )
    await cmd_brands(callback_query, state)


def register_handlers_brands(dp: Dispatcher):
    dp.register_callback_query_handler(
        cmd_brands,
        lambda c: c.data == 'brands',
        state=[UserFilters.choosing_brand, None]
    )
    dp.register_callback_query_handler(brand_chosen, state=UserFilters.choosing_brand)
    dp.register_callback_query_handler(brand_error, state=UserFilters.choosing_brand)
