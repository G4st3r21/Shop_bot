from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.models import Category
from tg_bot.db_session import session_db
from handlers.default import default_message
from keys.category import generate_category_buttons
from states import UserFilters


@session_db
async def cmd_category(callback_query: CallbackQuery, state: FSMContext, session: AsyncSession, category_list=None):
    await callback_query.answer()
    if not category_list:
        category_list = await Category.get_all(session)
        category_types_kb = await generate_category_buttons(category_list)
    else:
        category_types_kb = await generate_category_buttons(category_list, child=True)

    await callback_query.message.edit_text("Выберите категорию: ", reply_markup=category_types_kb)
    await state.set_state(UserFilters.choosing_category)


@session_db
async def category_chosen(callback_query: CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback_query.answer()

    category = callback_query.data
    if category == 'delete':
        await state.update_data(chosen_category=None)
    elif category != 'back':
        category_id = await Category.get_id(session, category)
        sub_category_list = await Category.get_child(session, category_id)
        await state.update_data(chosen_category=category)
        if sub_category_list:
            await cmd_category(callback_query, state, category_list=sub_category_list)
        else:
            await default_message(callback_query, state)


async def category_error(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await callback_query.message.answer(
        text="Я такого бренда не знаю, попробуйте еще раз"
    )
    await cmd_category(callback_query, state)


def register_handlers_category(dp: Dispatcher):
    dp.register_callback_query_handler(
        cmd_category, lambda c: c.data == 'categories',
        state=[UserFilters.choosing_category, None]
    )
    dp.register_callback_query_handler(category_chosen, state=UserFilters.choosing_category)
    dp.register_callback_query_handler(category_error, state=UserFilters.choosing_category)
