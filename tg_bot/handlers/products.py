from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, MediaGroup, InputFile, Message
from sqlalchemy.ext.asyncio import AsyncSession

from keys.products import generate_product_keyboard
from states import UserFilters
from db_session import session_db
from models import Product, Seller, Picture


async def get_product_media_group(pictures):
    if not pictures:
        return False

    media = MediaGroup()
    for picture in pictures:
        if not picture.file_id:
            media.attach_photo(InputFile('static/img/' + picture.link))
        else:
            media.attach_photo(picture.file_id)

    return media


async def set_picture_file_id(session, pictures: list[Picture], message: list[Message]):
    for i in range(len(message)):
        file_id = message[i].photo[-1]["file_id"]
        await pictures[i].set_file_id(session, pictures[i].id, file_id)


@session_db
async def show_products(callback_query: CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback_query.answer()
    user_data = await state.get_data()
    chosen_gender = user_data['chosen_gender'] if 'chosen_gender' in user_data else []
    chosen_categories = user_data['chosen_categories'] if 'chosen_categories' in user_data else []
    chosen_brands = user_data['chosen_brands'] if 'chosen_brands' in user_data else []
    if 'offset' not in user_data:
        offset = 0
    else:
        offset = user_data['offset']

    if offset == 0:
        await callback_query.message.delete()

    product_list = await Product.get_all(session, chosen_gender, chosen_categories, chosen_brands,
                                         offset, 5)
    offset += len(product_list)
    await state.update_data(offset=offset)

    full_count = await Product.get_all(session, chosen_gender, chosen_categories, chosen_brands, need_count=True)
    await state.update_data(full_count=full_count)

    if not product_list:
        all_product_kb = generate_product_keyboard(need_menu_button=True, need_more_button=False)
        await callback_query.message.answer("Больше товаров по выбранным фильтрам нет", reply_markup=all_product_kb)

    for product in product_list:
        seller_link = await Seller.get_link(session, product.seller_id)

        if product != product_list[-1]:
            all_product_kb = generate_product_keyboard(seller_link)
        elif user_data.get('full_count') and offset+5 > user_data['full_count']:
            all_product_kb = generate_product_keyboard(seller_link, need_menu_button=True)
        else:
            all_product_kb = generate_product_keyboard(seller_link, need_menu_button=True)

        pictures = await Picture.get(session, product.id)
        media = await get_product_media_group(pictures)
        if media:
            message = await callback_query.message.answer_media_group(media)
            await set_picture_file_id(session, pictures, message)
        else:
            await callback_query.message.answer(text="Изображений нет")
        await callback_query.message.answer(
            text=f"{product.title}\n\n"
                 f"Описание: {product.description}",
            reply_markup=all_product_kb
        )

    await UserFilters.choosing_product.set()


def register_handlers_products(dp: Dispatcher):
    dp.register_callback_query_handler(
        show_products,
        lambda c: c.data in ['products', 'next'],
        state=[UserFilters.choosing_product, None]
    )
