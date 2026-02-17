import asyncio
import logging
import os

from pyrogram import idle

from config import bot
from unu.db import close_database, connect_database
from unu.utils import load_all, save_all
from unu.version import ascii_art

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


async def main():
    os.system("cls" if os.name == "nt" else "clear")
    print(ascii_art)
    await connect_database()    await bot.start()
    print(f"Bot started as @{bot.me.username}")
    print(f"Registered {sum(len(g) for g in bot.dispatcher.groups.values())} handlers in {len(bot.dispatcher.groups)} groups")
    await load_all()

    await idle()

    await save_all()
    await bot.stop()
    await close_database()


if __name__ == "__main__":
    asyncio.run(main())
