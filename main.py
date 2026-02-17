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
    print(f"Bot started as @{bot.me.username}")
    await load_all()

    await idle()

    await save_all()
    await bot.stop()
    await close_database()


if __name__ == "__main__":
    asyncio.run(main())
