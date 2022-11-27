from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from models import Category
from db_session import session_db
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


async def check_all_child(session: AsyncSession, all_categories):
    for category in all_categories:
        child = await Category.get_all(session, category.id)
        if child:
            all_categories += await check_all_child(session, child)

    return all_categories


async def check_parents_is_chosen(session: AsyncSession, chosen_categories: list):  # ДОДУМАТЬ
    db_category_parent = []
    db_category = await Category.get_object(session, chosen_categories[0])
    if db_category.parent:
        db_category_parent.append(await Category.get_all(session, db_category.parent))

    for parent in db_category_parent[0]:
        child = [child.title for child in await Category.get_all(session, parent.parent)]
        if child in chosen_categories:
            chosen_categories.append((await Category.get_object(session, parent.id)).title)


async def get_all_categories(session: AsyncSession, user_data, parent_id=None):
    all_categories = await Category.get_all(session, parent_id)
    all_categories = [category.title for category in await check_all_child(session, all_categories)]

    chosen_categories: list = user_data['chosen_categories'] if 'chosen_categories' in user_data.keys() else []

    if sorted(all_categories) == sorted(chosen_categories):
        for category in all_categories:
            chosen_categories.remove(category)
    else:
        chosen_categories += all_categories

    await check_parents_is_chosen(session, chosen_categories)
    chosen_categories = list(set(chosen_categories))

    return chosen_categories


@session_db
async def category_chosen(callback_query: CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback_query.answer()
    user_data = await state.get_data()

    category = callback_query.data
    chosen_categories = user_data['chosen_categories'] if 'chosen_categories' in user_data.keys() else []
    parent_category = user_data['parent_category'] if 'parent_category' in user_data.keys() else None

    if category == 'delete':
        await state.update_data(chosen_categories=[])
        await cmd_category(callback_query, state)
    elif category != 'back':
        category_id = (await Category.get_object(session, category)).id if category != 'all' else None
        if category_id:
            sub_category_list = await Category.get_all(session, category_id)
        else:
            sub_category_list = []

        if category == 'all':
            parent_id = (await Category.get_object(session, parent_category)).id
            chosen_categories = await get_all_categories(session, user_data, parent_id)
        elif sub_category_list:
            await state.update_data(parent_category=category)
        elif category in chosen_categories:
            chosen_categories.remove(category)
        else:
            chosen_categories.append(category)

        await state.update_data(chosen_categories=chosen_categories)
        await cmd_category(callback_query, state, category_list=sub_category_list)


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
