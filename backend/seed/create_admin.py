import os
import sys
import uuid
from datetime import datetime

from sqlalchemy import text

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from interviews.core.jwt_auth import get_password_hash
from interviews.infrastructure.database.connection import async_session_maker


async def user() -> None:
    print("\nRun script[admin loaded].")
    password = os.getenv("ADMIN_PASSWORD")
    if password is None:
        raise ValueError("нет данных для ADMIN_PASSWORD в переменных окружения проекта.")
    hash_password: str | None = get_password_hash(password)
    email = os.getenv("ADMIN_EMAIL")
    id = uuid.uuid4()
    async with async_session_maker() as session:
        query = text(
            """
            INSERT INTO public.users (id, email, password, role_id, is_active, date_create, date_update)
            VALUES (:id, :email, :password, :role_id, :is_active, :date_create, :date_update)
            ON CONFLICT (email) DO NOTHING
        """
        )
        values = {
            "id": id,
            "email": email,
            "password": hash_password,
            "role_id": 2,
            "is_active": True,
            "date_create": datetime.now(),
            "date_update": datetime.now(),
        }
        await session.execute(query, values)
        await session.commit()
    print("admin loaded!\n")
