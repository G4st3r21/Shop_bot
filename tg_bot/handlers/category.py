from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from models import Category
from db_session import session_db
from handlers.default import default_message
from keys.category import generate_category_buttons
from states import UserFilters


@session_db
async def cmd_category(callback_query: CallbackQuery, state: FSMContext, session: AsyncSession, category_list=None):
    await callback_query.answer()
    user_data = await state.get_data()
    if not category_list:
        category_list = await Category.get_all(session)
        category_types_kb = await generate_category_buttons(category_list, user_data.get('chosen_categories', []))
    else:
        category_types_kb = await generate_category_buttons(category_list, user_data.get('chosen_categories', []),
                                                            child=True)

    await callback_query.message.edit_text("Выберите категорию: ", reply_markup=category_types_kb)
    await state.set_state(UserFilters.choosing_category)


@session_db
async def category_chosen(callback_query: CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback_query.answer()
    user_data = await state.get_data()

    category = callback_query.data
    chosen_categories = user_data['chosen_categories'] if 'chosen_categories' in user_data.keys() else []
    if category == 'delete':
        await state.update_data(chosen_category=None)
    elif category != 'back':
        category_id = await Category.get_id(session, category)
        sub_category_list = await Category.get_child(session, category_id)
        if category in chosen_categories:
            chosen_categories.remove(category)
        else:
            chosen_categories.append(category)
        await state.update_data(chosen_categories=chosen_categories)
        if sub_category_list:
            await cmd_category(callback_query, state, category_list=sub_category_list)
        else:
            await cmd_category(callback_query, state)


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
