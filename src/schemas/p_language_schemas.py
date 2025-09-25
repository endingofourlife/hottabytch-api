from pydantic import BaseModel


# Requests
class CreateLanguageRequest(BaseModel):
    name: str
    description: str
    picture: str
    level: str
    popularity: int

# Responses
class LanguageResponse(BaseModel):
    id: int
    name: str
    description: str
    picture: str
    level: str
    popularity: int