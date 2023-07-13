from fastapi import Depends
from pydantic import EmailStr
from sqlalchemy.orm import Session
from libgravatar import Gravatar
from redis.asyncio import Redis

from src.database.db import get_db
from src.database.redis_db import get_async_redis_client
from src.database.models import User
from src.schemas.users import UserModel



async def get_user_by_email(email: EmailStr, db: Session):
    user = db.query(User).filter_by(email=email).first()
    return user


async def create_user(body: UserModel, db: Session = Depends(get_db)):
    avatar = None

    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)

    user = User(**body.dict(), avatar=avatar)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


async def update_token(user: User, token: str | None, db: Session = Depends(get_db)):
    user.refresh_token = token
    db.commit()


async def confirme_email(email: str, db: Session) -> None:
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email, url: str, db: Session) -> User:
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    redis_client = await get_async_redis_client()
    await redis_client.delete(f"user:{email}")
    return user