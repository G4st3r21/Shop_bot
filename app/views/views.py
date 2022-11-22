import os
from typing import Any

from sqladmin._queries import Query

from models import Brand, Category, Picture, Seller, Product
from sqladmin import ModelView


class BrandView(ModelView, model=Brand):
    name = "Бренд"
    name_plural = "Бренды"
    column_list = [Brand.id, Brand.title]


class CategoryView(ModelView, model=Category):
    name = "Категория"
    name_plural = "Категории"
    column_list = [Category.id, Category.title]
    form_include_pk = True
    form_excluded_columns = ["id"]


class SellerView(ModelView, model=Seller):
    name = "Продавец"
    name_plural = "Продавцы"
    column_list = [Seller.id, Seller.link]


class ProductView(ModelView, model=Product):
    name = "Товар"
    name_plural = "Товары"
    column_list = [Product.id, Product.title]
    form_include_pk = True
    form_excluded_columns = ["id"]


class PictureView(ModelView, model=Picture):
    name = "Изображение"
    name_plural = "Изображения"

    column_list = [Picture.id, Picture.link]
    form_include_pk = True
    form_excluded_columns = ["id", "link"]

    create_template = 'upload_pictures.html'
    details_template = 'details_pictures.html'

    can_create = True
    can_edit = False

    async def delete_model(self, obj: Any) -> None:
        os.remove('static/img/' + obj.link)
        await Query(self).delete(obj)
