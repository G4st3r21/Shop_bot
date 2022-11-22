from db_session import SqlAlchemyBase
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Table


class Brand(SqlAlchemyBase):
    __tablename__ = 'brands'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False, unique=True)


class Category(SqlAlchemyBase):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, autoincrement=True)
    level = Column(Integer, nullable=False)
    parent = Column(Integer, ForeignKey("categories.id"), nullable=True)
    title = Column(String, nullable=False, unique=True)


class Seller(SqlAlchemyBase):
    __tablename__ = 'sellers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    link = Column(String, nullable=False, unique=True)


class Picture(SqlAlchemyBase):
    __tablename__ = 'pictures'
    id = Column(Integer, primary_key=True, autoincrement=True)
    parent_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    link = Column(String, nullable=False)


class Product(SqlAlchemyBase):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    brand_id = Column(Integer, ForeignKey(Brand.id), nullable=False)
    category_id = Column(Integer, ForeignKey(Category.id), nullable=False)
    male = Column(Boolean, nullable=False)
    seller_id = Column(Integer, ForeignKey(Seller.id), nullable=False)
    is_sold = Column(Boolean, nullable=False)


class BotUser(SqlAlchemyBase):
    __tablename__ = 'bot_users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_tg_id = Column(Integer, nullable=False)
    save_parameters = Column(Boolean, nullable=False, default=True)
    category_id = Column(Integer, ForeignKey(Category.id), nullable=True)
    sex_type = Column(Boolean, nullable=True)


user_brand = Table(
    'user_brands', SqlAlchemyBase.metadata,
    Column('user_id', Integer, ForeignKey(BotUser.id)),
    Column('brand_id', Integer, ForeignKey(Brand.id))
)
