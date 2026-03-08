import asyncio
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from seed.create_admin import user as admin_loaded
from seed.create_interviews import interviews as interviews_loaded
from seed.create_plans import plans as plans_loaded
from seed.create_roles import role as roles_loaded


async def main() -> None:
    try:
        await roles_loaded()
        await admin_loaded()
        await plans_loaded()
        await interviews_loaded()

    except Exception as err:
        print(err)


if __name__ == "__main__":
    asyncio.run(main())
