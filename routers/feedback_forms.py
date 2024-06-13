import logging
from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends

from app_databases.database import database, feedback_form_table, user_table
from pydantic_models.feedback_form_model import FeedbackForm, FeedbackFormEdit
from pydantic_models.user_model import User
from security import super_admin_or_admin_required, get_current_user_from_token

router = APIRouter()

logger = logging.getLogger(__name__)


async def check_if_form_already_exists(type_name: str):
    if await database.fetch_one(feedback_form_table.select().where(feedback_form_table.c.title == type_name)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This form already exists")


@router.post(
    "/feedback_form",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(super_admin_or_admin_required)],
    description="this is a create feedback form api, description",
)
async def add_a_feedback_form(feedback_form: FeedbackForm,
                              current_user: Annotated[User, Depends(get_current_user_from_token, ),], ):
    logger.info(f"Adding a new feedback_form : {feedback_form.title}")
    if not await check_if_form_already_exists(feedback_form.title):
        await database.execute(
            feedback_form_table.insert().values(title=feedback_form.title,
                                                created_by=current_user.id))
        return {
            "message": f"{feedback_form.title} added successfully",
        }


@router.get(
    "/feedback_form",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(super_admin_or_admin_required)],
)
async def get_all_feedback_forms():
    logger.info("Fetching all the feedback forms")
    forms = await database.fetch_all(feedback_form_table.select())
    return [
        {
            "id": single_form.id,
            "title": single_form.title,
            "created_by": await user_who_created_form(user_id=single_form.created_by)
        } for single_form in
        forms
    ]


async def user_who_created_form(user_id: int) -> str:
    user = await database.fetch_one(
        user_table.select().where(user_table.c.id == user_id))
    if not user:
        return ""
    else:
        return user.email


@router.put(
    "/feedback_form",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(super_admin_or_admin_required)],
)
async def update_a_feedback_form(feedback_form: FeedbackFormEdit,
                                 current_user: Annotated[User, Depends(get_current_user_from_token)], ):
    logger.info("Updating feedback form")
    await database.execute(
        feedback_form_table.update().values(title=feedback_form.title, created_by=current_user.id).where(
            feedback_form_table.c.id == feedback_form.id))

    updated_form = await database.fetch_one(
        feedback_form_table.select().where(feedback_form_table.c.id == feedback_form.id))
    return {
        "id": updated_form.id,
        "title": updated_form.title,
        "created_by": updated_form.created_by,
    }


@router.delete(
    "/feedback_form",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(super_admin_or_admin_required)],
)
async def delete_a_feedback_form(question_type_id: int):
    logger.info("Deleting a feedback form")
    deleted_form = await database.execute(
        feedback_form_table.delete().where(feedback_form_table.c.id == question_type_id))

    if deleted_form == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Form not found")
    elif deleted_form > 1:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting Form")
    else:
        return {
            "details": "Form deleted successfully",
        }
