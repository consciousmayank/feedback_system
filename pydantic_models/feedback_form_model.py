from typing import Optional

from pydantic import BaseModel


class FeedbackForm(BaseModel):
    title: str


class FeedbackFormEdit(FeedbackForm):
    id: int
    created_by: int
