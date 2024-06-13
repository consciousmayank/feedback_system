import logging

from fastapi import APIRouter, HTTPException, status, Depends

from app_databases.database import user_table, database, role_table
from pydantic_models.user_model import UserIn, UserInWithRole
from security import get_user, get_password_hash, authenticate_user, create_access_token, super_admin_required

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post(
    "/register/user",
    status_code=status.HTTP_201_CREATED
)
async def register_user_with_a_role(user: UserInWithRole):
    return await register_user(user=user, role_id=user.role_id)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED
)
async def register_a_user(user: UserIn):
    end_user_id = (await database.fetch_one(role_table.select().where(role_table.c.name == "endUser", ))).id
    return await register_user(user=user, role_id=end_user_id)


@router.get(
    "/user",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(super_admin_required)]
)
async def get_all_end_users_list(
        dependencies=None
):
    if dependencies is None:
        dependencies = [Depends(super_admin_required)]
    all_users = await database.fetch_all(user_table.select())
    return [
        {
            "id": singleUser.id,
            "email": singleUser.email,
            "role": (await database.fetch_one(role_table.select().where(role_table.c.id == singleUser.role_id))).name
        } for singleUser in all_users
    ]


# async def get_end_user():
#     if len(await get_all_end_users()) == 0:
#         # there are no end_user role yet in db. So add it.
#         return await database.execute(role_table.insert().values(name="endUser", ))
#     else:
#         return (await database.fetch_one(role_table.select().where(role_table.c.name == "endUser", ))).id
#
#
# async def get_admin():
#     if len(await database.fetch_all(role_table.select().where(role_table.c.name == "admin", ))) == 0:
#         return await database.execute(role_table.insert().values(name="admin", ))
#     else:
#         return (await database.fetch_one(role_table.select().where(role_table.c.name == "admin", ))).id
#
#
# async def get_super_admin():
#     if len(await database.fetch_all(role_table.select().where(role_table.c.name == "superAdmin", ))) == 0:
#         return await database.execute(role_table.insert().values(name="superAdmin", ))
#     else:
#         return (await database.fetch_one(role_table.select().where(role_table.c.name == "superAdmin", ))).id


@router.post(
    "/token",
    status_code=status.HTTP_200_OK
)
async def login(user: UserIn):
    user = await authenticate_user(email=user.email, password=user.password)
    access_token = create_access_token(email=user.email)
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


async def register_user(user: UserIn, role_id: int):
    if await get_user(email=user.email):
        logger.error("User with this email already exists", )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    logger.info("Fetching user", )
    query = user_table.insert().values(email=user.email, password=get_password_hash(password=user.password, ),
                                       role_id=role_id, )
    logger.debug(query)
    await database.execute(query)
    logger.info("User created", )
    return {
        "detail": "User created"
    }

# async def get_all_end_users():
#     all_end_users = await database.fetch_all(role_table.select().where(role_table.c.name == "endUser", ))
#     return all_end_users
