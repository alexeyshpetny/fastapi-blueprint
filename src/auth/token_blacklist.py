import logging
from datetime import UTC, datetime

from src.cache.redis import cache_client
from src.core.settings import settings

logger = logging.getLogger(__name__)

_BLACKLIST_KEY_PREFIX = "token_blacklist:"


async def is_token_blacklisted(jti: str) -> bool:
    if not settings.CACHE_ENABLED or cache_client is None:
        return False

    try:
        key = f"{_BLACKLIST_KEY_PREFIX}{jti}"
        exists = await cache_client.exists(key)
        return bool(exists)
    except Exception as e:
        logger.error(f"Error checking token blacklist: {e}", exc_info=True)
        return False


async def blacklist_token(jti: str, expires_at: datetime) -> None:
    if not settings.CACHE_ENABLED or cache_client is None:
        logger.warning("Cache is disabled, cannot blacklist token")
        return

    try:
        key = f"{_BLACKLIST_KEY_PREFIX}{jti}"
        now = datetime.now(UTC)
        ttl_seconds = int((expires_at - now).total_seconds())
        if ttl_seconds > 0:
            await cache_client.setex(key, ttl_seconds, "1")
            logger.debug(f"Token blacklisted: {jti}, expires in {ttl_seconds}s")
    except Exception as e:
        logger.error(f"Error blacklisting token: {e}", exc_info=True)


async def revoke_all_user_tokens(user_id: int) -> None:
    if not settings.CACHE_ENABLED or cache_client is None:
        logger.warning("Cache is disabled, cannot revoke user tokens")
        return

    try:
        key = f"user_token_revoked:{user_id}"
        max_ttl = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        await cache_client.setex(key, max_ttl, str(int(datetime.now(UTC).timestamp())))
        logger.info(f"All tokens revoked for user {user_id}")
    except Exception as e:
        logger.error(f"Error revoking user tokens: {e}", exc_info=True)
