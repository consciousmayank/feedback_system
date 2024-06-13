from typing import Optional

from pydantic import BaseModel


class QuestionsOptions(BaseModel):
    question_id: int
    text: str
    description: Optional[str] = None


class QuestionsOptionsEdit(QuestionsOptions):
    id: int
