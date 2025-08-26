from sqlalchemy import select, update
from database.models import Users
from database.session import get_db



async def add(user_id: int):
    async with get_db() as session:
        try:
            user = Users(user_id=user_id, share_percent=100)
            session.add(user)
            await session.commit()
            await session.refresh(user)
        except Exception as e:
            print(e)


async def change_share(user_id: int, share_percent: int):
    async with get_db() as session:
        try:
            await session.execute(update(Users)
                                  .where(Users.user_id==user_id)
                                  .values(share_percent = share_percent)
                                  )
            await session.commit()
        except Exception as e:
            print(e)


async def check_user(user_id: int):
    async with get_db() as session:
        try:
            result = await session.execute(select(Users).where(Users.user_id == user_id))
            user = result.scalar_one_or_none()
            
            if user is None:
                return None
            
            return True
        except Exception as e:
            print(e)


async def check_user_share(user_id: int):
    async with get_db() as session:
        try:
            result = await session.execute(select(Users).where(Users.user_id == user_id))
            user = result.scalar_one_or_none()
            
            if user is None:
                return None
            
            print(user.share_percent)
            return user.share_percent
        except Exception as e:
            print(e)