import datetime
import logging
from typing import Annotated

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, ExpiredSignatureError, JWTError
from passlib.context import CryptContext

from app_databases.database import user_table, database, role_table
from config import config
from pydantic_models.user_model import User

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], )
oath2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # the endpoint name which creates the token

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"}
)

token_expired_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Token has expired",
    headers={"WWW-Authenticate": "Bearer"}
)


def access_token_expiry_minutes() -> int:
    return 30


def create_access_token(email: str):
    logger.info("Creating access token", extra={"email": email})
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=access_token_expiry_minutes(), )
    jwt_data = {"sub": email, "exp": expire}
    logger.info("algo :: ", extra={"algo": config.ALGORITHM})
    logger.info("key :: ", extra={"key": config.TOKEN_SECRET_KEY})
    logger.info("encoded_jwt")
    encoded_jwt = jwt.encode(jwt_data, key=config.TOKEN_SECRET_KEY, algorithm=config.ALGORITHM)
    # encoded_jwt = jwt.encode(jwt_data, 'secret', algorithm='HS256')
    return encoded_jwt


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_text_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_text_password, hashed_password)


async def get_user(email: str) -> dict:
    logger.debug("Fetching user from DB", extra={"email": email})
    query = user_table.select().where(user_table.c.email == email)
    logger.debug("Query", extra={"query": query})
    return await database.fetch_one(query)


async def authenticate_user(email: str, password: str):
    logger.debug("Authenticating user", extra={"email": email})
    user = await get_user(email)
    if not user:
        raise credentials_exception
    if not verify_password(password, user.password):
        raise credentials_exception
    return user


async def get_current_user_from_token(token: Annotated[str, Depends(oath2_scheme)]):
    try:
        payload = jwt.decode(token, key=config.TOKEN_SECRET_KEY, algorithms=[config.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except ExpiredSignatureError as error:
        raise token_expired_exception from error
    except JWTError as error:
        raise credentials_exception from error
    user = await get_user(email=email)
    if user is None:
        raise credentials_exception
    return user


async def super_admin_required(
        current_user: User = Depends(get_current_user_from_token),  # Optional dependency injection
):
    super_admin_role = await database.fetch_one(
        role_table.select().where(role_table.c.name == "superAdmin")
    )

    # Fetch user from the database and compare the role
    user_in_db = await database.fetch_one(
        user_table.select().where(user_table.c.id == current_user.id)  # replace id with correct attribute name
    )

    if user_in_db.role_id != super_admin_role.id:  # Replace role_id with your actual attribute
        raise HTTPException(status_code=403, detail="Forbidden - Super Admin access required.")

    return current_user


async def admin_required(
        current_user: User = Depends(get_current_user_from_token),  # Optional dependency injection
):
    admin_role = await database.fetch_one(
        role_table.select().where(role_table.c.name == "admin")
    )

    # Fetch user from the database and compare the role
    user_in_db = await database.fetch_one(
        user_table.select().where(user_table.c.id == current_user.id)  # replace id with correct attribute name
    )

    if user_in_db.role_id != admin_role.id:  # Replace role_id with your actual attribute
        raise HTTPException(status_code=403, detail="Forbidden - Admin access required.")

    return current_user


async def super_admin_or_admin_required(
        current_user: User = Depends(get_current_user_from_token),  # Optional dependency injection
):
    admin_role = await database.fetch_one(
        role_table.select().where(role_table.c.name == "admin")
    )

    super_admin_role = await database.fetch_one(
        role_table.select().where(role_table.c.name == "superAdmin")
    )

    user_in_db = await database.fetch_one(
        user_table.select().where(user_table.c.id == current_user.id)  # replace id with correct attribute name
    )

    if user_in_db.role_id == admin_role.id or user_in_db.role_id == super_admin_role.id:
        return current_user
    else:
        raise HTTPException(status_code=403, detail="Access denied.")


async def end_user_required(
        current_user: User = Depends(get_current_user_from_token),  # Optional dependency injection
):
    end_user_role = await database.fetch_one(
        role_table.select().where(role_table.c.name == "endUser")
    )

    # Fetch user from the database and compare the role
    user_in_db = await database.fetch_one(
        user_table.select().where(user_table.c.id == current_user.id)  # replace id with correct attribute name
    )

    if user_in_db.role_id != end_user_role.id:  # Replace role_id with your actual attribute
        raise HTTPException(status_code=403, detail="Forbidden - end user access required.")

    return current_user


async def is_super_admin(
        current_user: User = Depends(get_current_user_from_token),  # Optional dependency injection
) -> bool:
    super_admin_role = await database.fetch_one(
        role_table.select().where(role_table.c.name == "superAdmin")
    )

    # Fetch user from the database and compare the role
    user_in_db = await database.fetch_one(
        user_table.select().where(user_table.c.id == current_user.id)  # replace id with correct attribute name
    )

    if user_in_db.role_id == super_admin_role.id:  # Replace role_id with your actual attribute
        return True

    return False


async def is_admin(
        current_user: User = Depends(get_current_user_from_token),  # Optional dependency injection
) -> bool:
    admin_role = await database.fetch_one(
        role_table.select().where(role_table.c.name == "admin")
    )

    # Fetch user from the database and compare the role
    user_in_db = await database.fetch_one(
        user_table.select().where(user_table.c.id == current_user.id)  # replace id with correct attribute name
    )

    if user_in_db.role_id == admin_role.id:  # Replace role_id with your actual attribute
        return True

    return False


async def is_end_user(
        current_user: User = Depends(get_current_user_from_token),  # Optional dependency injection
) -> bool:
    end_user_role = await database.fetch_one(
        role_table.select().where(role_table.c.name == "endUser")
    )

    # Fetch user from the database and compare the role
    user_in_db = await database.fetch_one(
        user_table.select().where(user_table.c.id == current_user.id)  # replace id with correct attribute name
    )

    if user_in_db.role_id == end_user_role.id:  # Replace role_id with your actual attribute
        return True

    return False
