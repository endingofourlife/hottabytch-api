from pydantic import BaseModel


# Requests
class CreateLanguageRequest(BaseModel):
    name: str

# Responses
class LanguageResponse(BaseModel):
    id: int
    name: str