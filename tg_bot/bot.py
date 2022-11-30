import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import config
from db_session import global_init
from handlers import register_handlers_brands
from handlers import register_handlers_category
from handlers import register_handlers_default
from handlers import register_handlers_gender
from handlers import register_handlers_products
from config import *

logger = logging.getLogger(__name__)


async def main():
    await global_init(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.info("Starting tg_bot")

    bot = Bot(token=config.TOKEN)
    dp = Dispatcher(bot, storage=MemoryStorage())

    register_handlers_brands(dp)
    register_handlers_category(dp)
    register_handlers_gender(dp)
    register_handlers_products(dp)
    register_handlers_default(dp)

    await dp.skip_updates()
    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
