from aiogram import Bot, Dispatcher
from datetime import datetime
from config import settings
from handlers.private import router as private_router
import logging
import asyncio

bot = Bot(token=settings.TG_BOT_API_TOKEN)
dp = Dispatcher()
dp.include_router(private_router)


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())