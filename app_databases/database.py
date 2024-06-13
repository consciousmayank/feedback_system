# Here the database schema is defined,
import databases
import sqlalchemy
from sqlalchemy import (TIMESTAMP, Column, Integer, String, Table,
                        func, Boolean, ForeignKey, )

from config import config

# BoilerPlate code #
metadata = sqlalchemy.MetaData()
# BoilerPlate code #

role_table = Table(
    "roles",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, unique=True),
    Column("created_at", TIMESTAMP, default=func.now()),
    Column("updated_at", TIMESTAMP, default=func.now(), onupdate=func.now()),
)

user_table = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String, unique=True),
    Column("password", String),
    Column("fcm_token", String),
    Column("verification_code", String, default=None),
    Column("confirmed", Boolean, default=False),
    Column("role_id", Integer, ForeignKey("roles.id"), nullable=False),
    Column("created_at", TIMESTAMP, default=func.now()),
    Column("updated_at", TIMESTAMP, default=func.now(), onupdate=func.now())
)

question_types_table = Table(
    "question_type",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("name", String, unique=True),
    Column("description", String, ),
    Column("created_by_user", Integer, ForeignKey("users.id"), nullable=False),
    Column("created_at", TIMESTAMP, default=func.now()),
    Column("updated_at", TIMESTAMP, default=func.now(), onupdate=func.now()),
)

feedback_form_table = Table(
    "feedback_forms",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("title", String),
    Column("created_by", Integer, ForeignKey("users.id")),  # Link to admin creator
    Column("created_at", TIMESTAMP, default=func.now()),
    Column("updated_at", TIMESTAMP, default=func.now(), onupdate=func.now())
)

question_table = Table(
    "questions",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("form_id", Integer, ForeignKey("feedback_forms.id")),
    Column("text", String),
    Column("description", String),
    Column("type", Integer, ForeignKey("question_type.id"), nullable=False),
)

options_table = Table(
    "options",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("question_id", Integer, ForeignKey("questions.id"), nullable=False),
    Column("text", String),
    Column("description", String),
)

response_table = Table(
    "answers",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("question_id", Integer, ForeignKey("questions.id")),
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("selected_answer", String),
    Column("user_input_answer", String),
    Column("rating", Integer, nullable=True),
)

profile_table = Table(
    "profiles",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("phone_number", String, ),
    Column("profile_picture", String),
    Column("user_id", ForeignKey("users.id"), nullable=False),
    Column("created_at", TIMESTAMP, default=func.now()),
    Column("updated_at", TIMESTAMP, default=func.now(), onupdate=func.now()),
)

connect_args = {"check_same_thread": False} if "sqlite" in config.DATABASE_URL else {}
engine = sqlalchemy.create_engine(
    config.DATABASE_URL, connect_args=connect_args
)

db_args = {"min_size": 1, "max_size": 3} if "postgres" in config.DATABASE_URL else {}

metadata.create_all(engine)
database = databases.Database(
    config.DATABASE_URL, force_rollback=config.DB_FORCE_ROLL_BACK, **db_args
)
# BoilerPlate code #
