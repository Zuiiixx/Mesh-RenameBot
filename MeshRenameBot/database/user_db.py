from ..core.get_config import get_var
import asyncio

async def get_user_db():
    is_mongo = await get_var("IS_MONGO")
    if is_mongo:
        from .mongo_impl import UserDB as UserDBImpl
    else:
        from .postgres_impl import UserDB as UserDBImpl
    return UserDBImpl