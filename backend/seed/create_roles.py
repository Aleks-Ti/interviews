import os
import sys

from sqlalchemy import text

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from interviews.infrastructure.database.connection import async_session_maker


async def role() -> None:
    print("\nRun script[roles loaded].")
    
    roles_data = [
        {
            "id": 2,
            "name": "admin"
        },
        {
            "id": 3,
            "name": "reader"
        }
    ]
    
    async with async_session_maker() as session:
        for role_data in roles_data:
            query = text(
                """
                INSERT INTO public.roles (
                    id,
                    name
                )
                VALUES (
                    :id,
                    :name
                )
                RETURNING id
            """
            )
            values = {
                "id": role_data["id"],
                "name": role_data["name"]
            }
            await session.execute(query, values)
        await session.commit()
        print("roles loaded!\n")
