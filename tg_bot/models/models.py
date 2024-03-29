from sqlalchemy.ext.asyncio import AsyncSession

from db_session import SqlAlchemyBase
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Table, select, update, func, desc


class Brand(SqlAlchemyBase):
    __tablename__ = 'brands'
    __table_args__ = {"extend_existing": True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False, unique=True)

    @classmethod
    async def get_all(cls, session: AsyncSession):
        _ = await session.execute(select(cls))
        return _.scalars().all()

    @classmethod
    async def get_all_id(cls, session: AsyncSession, brand_list: list[str]):
        if len(brand_list) < 0:
            return []

        brand_id_list = [
            (
                await session.execute(select(cls).where(cls.title == brand_title))
            ).scalar().id for brand_title in brand_list
        ]
        return brand_id_list


class Category(SqlAlchemyBase):
    __tablename__ = 'categories'
    __table_args__ = {"extend_existing": True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    level = Column(Integer, nullable=False)
    parent = Column(Integer, ForeignKey("categories.id"), nullable=True)
    title = Column(String, nullable=False, unique=True)

    @classmethod
    async def get_object(cls, session: AsyncSession, title: str = None, id: int = None):
        if title:
            _ = await session.execute(select(cls).where(cls.title == title))
        else:
            _ = await session.execute(select(cls).where(cls.id == id))
        return _.scalar()

    @classmethod
    async def get_all(cls, session: AsyncSession, parent_id=None):
        _ = await session.execute(select(cls).where(cls.parent == parent_id))
        return _.scalars().all()

    @classmethod
    async def get_all_id(cls, session: AsyncSession, category_list):
        if len(category_list) < 0:
            return []

        category_id_list = [
            (
                await session.execute(select(cls).where(cls.title == category_title))
            ).scalar().id for category_title in category_list
        ]
        return category_id_list


class Seller(SqlAlchemyBase):
    __tablename__ = 'sellers'
    __table_args__ = {"extend_existing": True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    link = Column(String, nullable=False, unique=True)

    @classmethod
    async def get_link(cls, session: AsyncSession, id: int):
        _ = await session.execute(select(cls.link).where(cls.id == id))
        return _.scalar()


class Picture(SqlAlchemyBase):
    __tablename__ = 'pictures'
    __table_args__ = {"extend_existing": True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    parent_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    link = Column(String, nullable=False)
    file_id = Column(String, nullable=True)

    @classmethod
    async def get(cls, session: AsyncSession, id: int):
        _ = await session.execute(select(cls).where(cls.parent_id == id))
        return _.scalars().all()

    @classmethod
    async def set_file_id(cls, session: AsyncSession, picture_id, file_id):
        _ = await session.execute(update(cls).where(cls.id == picture_id).values(file_id=file_id))
        await session.commit()


class Product(SqlAlchemyBase):
    __tablename__ = 'products'
    __table_args__ = {"extend_existing": True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    brand_id = Column(Integer, ForeignKey(Brand.id), nullable=False)
    category_id = Column(Integer, ForeignKey(Category.id), nullable=False)
    male = Column(Boolean, nullable=False)
    seller_id = Column(Integer, ForeignKey(Seller.id), nullable=False)
    is_sold = Column(Boolean, nullable=False)

    @classmethod
    async def get(cls, session: AsyncSession, id: int):
        _ = await session.execute(select(cls).where(cls.id == id))

        return _.scalar()

    @classmethod
    async def get_all(cls, session: AsyncSession, chosen_gender, chosen_categories, chosen_brands, offset=0, limit=None,
                      need_count=False):
        categories_id = await Category.get_all_id(session, chosen_categories) if chosen_categories else None
        brands_id = await Brand.get_all_id(session, chosen_brands) if chosen_brands else None

        if not need_count:
            query = select(cls).where(cls.is_sold == False).offset(offset).limit(limit).order_by(desc(cls.id))
        else:
            query = select([func.count()]).select_from(cls).where(cls.is_sold == False)
        if brands_id:
            query = query.where(cls.brand_id.in_(brands_id))
        if chosen_gender:
            gender = True if chosen_gender == 'мужской' else False
            query = query.where(cls.male == gender)
        if categories_id:
            query = query.where(cls.category_id.in_(categories_id))

        _ = await session.execute(query)

        if not need_count:
            return _.scalars().all()
        else:
            return _.scalar()


class BotUser(SqlAlchemyBase):
    __tablename__ = 'bot_users'
    __table_args__ = {"extend_existing": True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_tg_id = Column(Integer, nullable=False)
    save_parameters = Column(Boolean, nullable=False, default=True)
    category_id = Column(Integer, ForeignKey(Category.id), nullable=True)
    sex_type = Column(Boolean, nullable=True)


user_brand = Table(
    'user_brands', SqlAlchemyBase.metadata,
    Column('user_id', Integer, ForeignKey(BotUser.id)),
    Column('brand_id', Integer, ForeignKey(Brand.id)),
    extend_existing=True
)
