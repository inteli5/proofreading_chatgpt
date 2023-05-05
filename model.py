from pydantic import BaseModel


class OriginalText(BaseModel):
    text: str


class CorrectedText(BaseModel):
    corrected_text: str
    diff: str
    time_used: str


class User(BaseModel):
    username: str
    password: str


class TokenData(BaseModel):
    username: str | None = None
