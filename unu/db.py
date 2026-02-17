import json
import logging

import redis.asyncio as aioredis
from tortoise import Tortoise, fields
from tortoise.models import Model

from config import DB_HOST, DB_PORT, DB_USERNAME, DB_PASSWORD, DB_DATABASE, REDIS_URL

logger = logging.getLogger(__name__)

# --- Redis client (singleton) ---
_redis: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(
            REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=10,
        )
    return _redis


async def close_redis():
    global _redis
    if _redis:
        await _redis.aclose()
        _redis = None


# --- Redis cache helpers ---
CACHE_TTL = 300  # 5 minutes


async def cache_get(key: str):
    r = await get_redis()
    val = await r.get(key)
    if val is not None:
        return json.loads(val)
    return None


async def cache_set(key: str, value, ttl: int = CACHE_TTL):
    r = await get_redis()
    await r.set(key, json.dumps(value), ex=ttl)


async def cache_delete(key: str):
    r = await get_redis()
    await r.delete(key)


# --- ORM Models ---

class Chat(Model):
    id = fields.BigIntField(pk=True)
    theme = fields.CharField(max_length=255, default="classic")
    bluff = fields.BooleanField(default=True)
    seven = fields.BooleanField(default=False)
    one_win = fields.BooleanField(default=False)
    one_card = fields.BooleanField(default=False)
    lang = fields.CharField(max_length=255, default="en-US")
    auto_pin = fields.BooleanField(default=False)
    satack = fields.BooleanField(default=True)
    draw_one = fields.BooleanField(default=True)

    class Meta:
        table = "chat"

    @classmethod
    async def get_cached(cls, chat_id: int):
        """Get chat from cache or DB."""
        key = f"chat:{chat_id}"
        cached = await cache_get(key)
        if cached:
            # Return a dict-like object with attribute access
            return _DictObj(cached)
        obj = await cls.get_or_none(id=chat_id)
        if obj:
            data = {
                "id": obj.id, "theme": obj.theme, "bluff": obj.bluff,
                "seven": obj.seven, "one_win": obj.one_win, "one_card": obj.one_card,
                "lang": obj.lang, "auto_pin": obj.auto_pin, "satack": obj.satack,
                "draw_one": obj.draw_one,
            }
            await cache_set(key, data)
        return obj

    @classmethod
    async def invalidate_cache(cls, chat_id: int):
        await cache_delete(f"chat:{chat_id}")


class User(Model):
    id = fields.BigIntField(pk=True)
    placar = fields.BooleanField(default=False)
    wins = fields.IntField(default=0)
    matches = fields.IntField(default=0)
    cards = fields.IntField(default=0)
    sudo = fields.BooleanField(default=False)
    lang = fields.CharField(max_length=255, default="en-US")

    class Meta:
        table = "user"

    @classmethod
    async def get_cached(cls, user_id: int):
        key = f"user:{user_id}"
        cached = await cache_get(key)
        if cached:
            return _DictObj(cached)
        obj = await cls.get_or_none(id=user_id)
        if obj:
            data = {
                "id": obj.id, "placar": obj.placar, "wins": obj.wins,
                "matches": obj.matches, "cards": obj.cards, "sudo": obj.sudo,
                "lang": obj.lang,
            }
            await cache_set(key, data)
        return obj

    @classmethod
    async def invalidate_cache(cls, user_id: int):
        await cache_delete(f"user:{user_id}")


class GameModel(Model):
    id = fields.IntField(pk=True)
    theme = fields.CharField(max_length=255)
    chat_id = fields.BigIntField(null=True)
    last_card = fields.JSONField(null=True)
    last_card_2 = fields.JSONField(null=True)
    next_player_id = fields.BigIntField(null=True)
    deck = fields.JSONField(null=True)
    players = fields.JSONField(null=True)
    is_started = fields.BooleanField(default=False)
    draw = fields.IntField(default=0)
    drawed = fields.BooleanField(default=False)
    chosen = fields.CharField(max_length=255, null=True)
    closed = fields.BooleanField(default=False)
    winner = fields.BooleanField(default=True)
    timer_duration = fields.IntField(default=30)
    message_id = fields.IntField(null=True)
    is_dev = fields.BooleanField(default=False)
    bluff = fields.BooleanField(default=False)

    class Meta:
        table = "game_model"


class GamePlayer(Model):
    id = fields.IntField(pk=True)
    player_id = fields.BigIntField()
    game_chat_id = fields.BigIntField()

    class Meta:
        table = "game_player"


class _DictObj:
    """Simple helper to access dict keys as attributes (for cached results)."""
    def __init__(self, d: dict):
        self.__dict__.update(d)

    def __getattr__(self, name):
        return self.__dict__.get(name)


async def connect_database():
    """Connect to TiDB via MySQL protocol and generate schemas."""
    db_url = (
        f"mysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"
        "?ssl=true"
    )
    logger.info("Connecting to TiDB at %s:%s/%s", DB_HOST, DB_PORT, DB_DATABASE)

    await Tortoise.init({
        "connections": {
            "bot_db": {
                "engine": "tortoise.backends.mysql",
                "credentials": {
                    "host": DB_HOST,
                    "port": DB_PORT,
                    "user": DB_USERNAME,
                    "password": DB_PASSWORD,
                    "database": DB_DATABASE,
                    "ssl": True,
                },
            },
        },
        "apps": {"bot": {"models": [__name__], "default_connection": "bot_db"}},
    })

    # Generate the schema (safe — creates tables if not exist)
    await Tortoise.generate_schemas(safe=True)

    # Test Redis connectivity
    try:
        r = await get_redis()
        await r.ping()
        logger.info("Redis connected successfully")
    except Exception as e:
        logger.warning("Redis connection failed, will run without cache: %s", e)


async def close_database():
    """Close DB and Redis connections."""
    await Tortoise.close_connections()
    await close_redis()
