import logging
from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends

from app_databases.database import database, question_types_table
from pydantic_models.question_type_model import QuestionType, QuestionTypeEdit
from pydantic_models.user_model import User
from security import super_admin_or_admin_required, get_current_user_from_token

router = APIRouter()

logger = logging.getLogger(__name__)


async def check_if_type_already_exists(type_name: str):
    if await database.fetch_one(question_types_table.select().where(question_types_table.c.name == type_name)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This question type already exists")


@router.post(
    "/question_type",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(super_admin_or_admin_required)],
)
async def add_a_question_type(question_type: QuestionType,
                              current_user: Annotated[User, Depends(get_current_user_from_token)], ):
    logger.info(f"Adding a new question type: {question_type.name}")
    if not await check_if_type_already_exists(question_type.name):
        await database.execute(
            question_types_table.insert().values(name=question_type.name, description=question_type.description,
                                                 created_by_user=current_user.id))
        return {
            "message": f"{question_type.name} added successfully",
        }


@router.get(
    "/question_type",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(super_admin_or_admin_required)],
)
async def get_all_question_types():
    logger.info("Fetching all the question types")
    types = await database.fetch_all(question_types_table.select())
    return [
        {"id": single_type.id, "name": single_type.name, "description": single_type.description} for single_type in
        types
    ]


@router.put(
    "/question_type",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(super_admin_or_admin_required)],
)
async def update_a_question_type(question_type: QuestionTypeEdit):
    logger.info("Updating question type")
    await database.execute(
        question_types_table.update().values(name=question_type.name, description=question_type.description).where(
            question_types_table.c.id == question_type.id))

    updated_question_type = await database.fetch_one(
        question_types_table.select().where(question_types_table.c.id == question_type.id))
    return {
        "id": updated_question_type.id,
        "name": updated_question_type.name,
        "description": updated_question_type.description,
    }


@router.delete(
    "/question_type",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(super_admin_or_admin_required)],
)
async def delete_a_question_type(question_type_id: int):
    logger.info("Deleting a question type")
    deleted_question_type_id = await database.execute(
        question_types_table.delete().where(question_types_table.c.id == question_type_id))

    if deleted_question_type_id == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question type not found")
    elif deleted_question_type_id > 1:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting question type")
    else:
        return {
            "details": "Question type deleted successfully",
        }
