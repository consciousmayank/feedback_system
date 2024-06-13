from typing import Optional

from pydantic import BaseModel


class QuestionType(BaseModel):
    name: str
    description: Optional[str] = None


class QuestionTypeEdit(QuestionType):
    id: int
