import logging

from fastapi import APIRouter, HTTPException, status, Depends

from app_databases.database import database, feedback_form_table, options_table, question_table
from pydantic_models.questions_option_model import QuestionsOptions, QuestionsOptionsEdit
from security import super_admin_or_admin_required

router = APIRouter()

logger = logging.getLogger(__name__)


# async def check_if_form_already_exists(type_name: str):
#     if await database.fetch_one(feedback_form_table.select().where(feedback_form_table.c.title == type_name)):
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This form already exists")


@router.post(
    "/questions_options",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(super_admin_or_admin_required)],
    description="This method is used to add a new option to a question",
)
async def add_a_questions_option(option: QuestionsOptions, ):
    logger.info(f"Adding a new option to question : {option.question_id}")
    await database.execute(
        options_table.insert().values(question_id=option.question_id, text=option.text, description=option.description))
    return {
        "message": f"{option.text} added successfully",
    }


@router.get(
    "/questions_options",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(super_admin_or_admin_required)],
    description="This method is used fetch all the options of a question",
)
async def get_all_options_of_a_question(question_id: int):
    logger.info(f"Fetching all the options for question {await parent_question_of_an_option(question_id=question_id)}")
    options = await database.fetch_all(options_table.select().where(options_table.c.question_id == question_id))
    return [
        {
            "id": single_option.id,
            "title": single_option.text,
            "description": single_option.description,
            "question": await parent_question_of_an_option(question_id=single_option.question_id),

        } for single_option in
        options
    ]


async def parent_question_of_an_option(question_id: int) -> str:
    question = await database.fetch_one(
        question_table.select().where(question_table.c.id == question_id))
    if not question:
        return ""
    else:
        return question.text


@router.put(
    "/questions_options",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(super_admin_or_admin_required)],
    description="This method is used update an option of a question",
)
async def update_a_questions_option(option: QuestionsOptionsEdit, ):
    logger.info(f"Updating an option of a question, {await parent_question_of_an_option(question_id=option.question_id)}")
    await database.execute(
        options_table.update().values(text=option.text, description=option.description).where(
            options_table.c.id == option.id))

    updated_option = await database.fetch_one(
        options_table.select().where(options_table.c.id == option.id))
    return {
        "id": updated_option.id,
        "text": updated_option.text,
        "description": updated_option.description,
    }


@router.delete(
    "/questions_options",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(super_admin_or_admin_required)],
    description="This method is used delete an option of a question",
)
async def delete_a_feedback_form(options_id: int):
    logger.info("Deleting an option")
    deleted_option = await database.execute(
        options_table.delete().where(options_table.c.id == options_id))

    if deleted_option == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Option not found")
    elif deleted_option > 1:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting Option")
    else:
        return {
            "details": "Option deleted successfully",
        }
