from contextlib import asynccontextmanager

from fastapi import FastAPI

from app_databases.database import database, role_table
from logging_conf import configure_logging
from routers.feedback_forms import router as feedback_forms_router
from routers.question_type import router as question_type_router
from routers.roles import router as roles_router
from routers.users import router as users_router
from routers.options_to_questions import router as question_options_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    await database.connect()
    if len(await database.fetch_all(role_table.select().where(role_table.c.name == "superAdmin", ))) == 0:
        await database.execute(role_table.insert().values(name="superAdmin", ))
    if len(await database.fetch_all(role_table.select().where(role_table.c.name == "admin", ))) == 0:
        await database.execute(role_table.insert().values(name="admin", ))
    if len(await database.fetch_all(role_table.select().where(role_table.c.name == "endUser", ))) == 0:
        await database.execute(role_table.insert().values(name="endUser", ))
    yield
    await database.disconnect()


version = "0.005"

app = FastAPI(lifespan=lifespan, version=version, summary="A Feedback System API",
              description="I am trying to make backend for an application which can be used to ask and submit feedbacks",
              contact={
                  "Name": "Mayank",
                  "Phone": "9611886339"
              }, title=f"Feedback System (v{version})")

app.include_router(users_router)
app.include_router(roles_router)
app.include_router(question_type_router)
app.include_router(feedback_forms_router)
app.include_router(question_options_router)
