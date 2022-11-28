from datetime import datetime
import aiofiles

from fastapi import FastAPI, UploadFile, File, Form
from sqladmin import Admin
from typing import List

from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette.staticfiles import StaticFiles

from admin_config import JWT_SECRET
from auth import CheckUser, decode_jwt
from db_session import global_init, create_session
from views import BrandView, CategoryView, SellerView, ProductView, PictureView
from models import SqlAlchemyBase, Picture
from admin_config import *

app = FastAPI()
engine = global_init(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)
authentication_backend = CheckUser(secret_key=JWT_SECRET)
admin = Admin(app, engine, authentication_backend=authentication_backend)
CategoryView.async_engine = engine

app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(SessionMiddleware, secret_key=JWT_SECRET)


@app.post("/upload_files")
async def upload_file(request: Request, parent_id: int = Form(), files: List[UploadFile] = File(...)):
    if not decode_jwt(request.session.get("token")):
        return Response(status_code=403)
    for file in files:
        new_filename = str(hash(file.filename.split(".")[0]))[:-3] + str(datetime.now().microsecond)[-1:-3]
        file_extension = file.filename.split(".")[1]
        file.filename = f"{new_filename}.{file_extension}"

        async with aiofiles.open('static/img/' + file.filename, "wb") as pic:
            await pic.write(await file.read())
        async with create_session() as session:
            db_picture = Picture(link=file.filename, parent_id=parent_id)
            session.add(db_picture)
            await session.commit()

    return RedirectResponse('/admin/picture/list', status_code=302)


async def init_models():
    async with engine.begin() as conn:
        # await conn.run_sync(SqlAlchemyBase.metadata.drop_all)
        await conn.run_sync(SqlAlchemyBase.metadata.create_all)


# asyncio.create_task(init_models())

admin.add_view(BrandView)
admin.add_view(CategoryView)
admin.add_view(SellerView)
admin.add_view(ProductView)
admin.add_view(PictureView)
