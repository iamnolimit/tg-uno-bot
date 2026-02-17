from pyrogram import Client

games = {}
player_game = {}
notify_dict = {}  # chat_id -> set of user_ids that want to be notified

timeout = 120
minimum_players = 2

sudoers = [123456789]

API_ID = "29753813"
API_HASH = "ac02ffebd360cfdd54619db26c6de17b"
BOT_TOKEN = "8269250023:AAHUjs-UrzuztIm-HDN2Az0H6GuC8-C6oG8"

# --- TiDB (MySQL-compatible) config ---
DB_HOST = "gateway01.ap-southeast-1.prod.aws.tidbcloud.com"
DB_PORT = 4000
DB_USERNAME = "2cpJE8CHAHeY8Ep.root"
DB_PASSWORD = "XqurMYLPt2NnK4Gx"
DB_DATABASE = "test"

# --- Redis config ---
REDIS_URL = "redis://default:zVu6TSmP7HT7iKmICJ4TwmVeMrEbJOGB@redis-14061.crce185.ap-seast-1-1.ec2.cloud.redislabs.com:14061"

# --- Telegram config ---
bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, plugins={"root": "unu.plugins"})
