import logging

from fastapi import APIRouter, HTTPException, status, Depends

from app_databases.database import database, role_table
from pydantic_models.role_model import Role, RoleUpdate
from security import is_super_admin, super_admin_required

router = APIRouter()

logger = logging.getLogger(__name__)


async def check_if_role_already_exists(role_name: str):
    if await database.fetch_one(role_table.select().where(role_table.c.name == role_name)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Role already exists")


@router.post(
    "/role",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(super_admin_required)],
)
async def add_a_new_role(role: Role):
    logger.info(f"Adding a new role: {role.name}")
    if not await check_if_role_already_exists(role.name):
        await database.execute(role_table.insert().values(name=role.name))
        return {
            "message": f"Role {role.name} added successfully",
        }


@router.get(
    "/role",
    status_code=status.HTTP_200_OK,
)
async def get_all_the_roles():
    logger.info("Fetching all the roles")
    roles = await database.fetch_all(role_table.select())
    return [
        {"id": role.id, "name": role.name} for role in roles
    ]


@router.put(
    "/role",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(super_admin_required)],
)
async def update_role(role: RoleUpdate):
    logger.info("Updating role")
    await database.execute(role_table.update().values(name=role.name).where(role_table.c.id == role.id))

    updated_role = await database.fetch_one(role_table.select().where(role_table.c.id == role.id))
    return {
        "roles": updated_role,
    }


@router.delete(
    "/role",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(is_super_admin)],
)
async def update_role(role_id: int):
    logger.info("Deleting role")
    deleted_role_id = await database.execute(role_table.delete().where(role_table.c.id == role_id))

    if deleted_role_id == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    elif deleted_role_id > 1:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting role")
    else:
        return {
            "detiails": f"Role deleted successfully",
        }
