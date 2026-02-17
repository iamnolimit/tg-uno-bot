import asyncio
import os

from pyrogram import idle

from config import bot
from unu.db import close_database, connect_database
from unu.utils import load_all, save_all
from unu.version import ascii_art


async def main():
    os.system("cls" if os.name == "nt" else "clear")
    print(ascii_art)
    await connect_database()
    await bot.start()
    await load_all()

    await idle()

    await save_all()
    await bot.stop()
    await close_database()


asyncio.run(main())
