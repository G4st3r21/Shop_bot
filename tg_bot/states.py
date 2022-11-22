from aiogram.dispatcher.filters.state import StatesGroup, State


class UserFilters(StatesGroup):
    choosing_gender = State(state="gender_state")
    choosing_brand = State(state="brand_state")
    choosing_category = State(state="category_state")
    choosing_product = State(state="product_state")
