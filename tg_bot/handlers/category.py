from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from models import Category
from db_session import session_db
from keys.category import generate_category_buttons
from states import UserFilters


@session_db
async def cmd_category(callback_query: CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback_query.answer()

    user_data = await state.get_data()
    parent_category = user_data['parent_category'] if 'parent_category' in user_data.keys() else None

    if not parent_category:
        category_list = await Category.get_all(session)
        category_types_kb = await generate_category_buttons(category_list, user_data.get('chosen_categories', []))
    else:
        parent_object = await Category.get_object(session, parent_category)
        category_list = await Category.get_all(session, parent_object.id)
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
    parent_category = user_data['parent_category'] if 'parent_category' in user_data.keys() else None

    if category == 'delete':
        await state.update_data(chosen_categories=[])
    elif category != 'back':
        category_obj = await Category.get_object(session, category) if category != 'all' else None
        sub_category_list = await Category.get_all(session, category_obj.id) if category_obj else []

        if category == 'all':
            if parent_category:
                parent_obj = await Category.get_object(session, parent_category)
                chosen_categories = await get_all_categories(session, user_data, parent_obj)
            else:
                chosen_categories = await get_all_categories(session, user_data)
        elif sub_category_list:
            await state.update_data(parent_category=category)
        elif category in chosen_categories:
            chosen_categories.remove(category)
        else:
            chosen_categories.append(category)

        await state.update_data(chosen_categories=chosen_categories)
    else:
        await state.update_data(parent_category=None)

    await cmd_category(callback_query, state)


async def get_all_categories(session: AsyncSession, user_data, parent=None):
    all_categories = await Category.get_all(session, parent.id) if parent else await Category.get_all(session)
    all_categories = [category.title for category in await check_all_child(session, all_categories)]

    chosen_categories: list = user_data['chosen_categories'] if 'chosen_categories' in user_data.keys() else []

    if sorted(all_categories) == sorted(chosen_categories):
        for category in all_categories:
            chosen_categories.remove(category)
    else:
        chosen_categories += all_categories

    if parent:
        chosen_categories.append(parent.title)
    chosen_categories = list(set(chosen_categories))

    return chosen_categories


async def check_all_child(session: AsyncSession, all_categories):
    for category in all_categories:
        child = await Category.get_all(session, category.id)
        if child:
            all_categories += await check_all_child(session, child)

    return all_categories


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
    dp.register_callback_query_handler(
        category_chosen, lambda c: c.data != 'menu',
        state=UserFilters.choosing_category
    )
    dp.register_callback_query_handler(
        category_error, lambda c: c.data != 'menu',
        state=UserFilters.choosing_category
    )
