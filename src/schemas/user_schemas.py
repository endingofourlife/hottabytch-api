from pydantic import BaseModel


# Base schemas
class ActiveLanguage(BaseModel):
    language_id: int
    name: str

class UserBase(BaseModel):
    user_id: int
    first_name: str
    streak: int
    xp: int
    active_language: ActiveLanguage | None = None
    timezone: str
    is_streak: bool


# REQUESTS
class UserAuthRequest(BaseModel):
    user_id: int
    first_name: str
    timezone: str | None = None
    hash: str

class LanguageUpdateRequest(BaseModel):
    language_id: int

# RESPONSES
class UserAuthResponse(BaseModel):
    # access_token: str
    user: UserBase

class LanguageUpdateResponse(BaseModel):
    success: bool