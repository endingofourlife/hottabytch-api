from typing import Generic, TypeVar, Optional

from pydantic import BaseModel

T = TypeVar('T')

class ServiceResult(BaseModel, Generic[T]):
    is_success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    status_code: Optional[int] = None

    @classmethod
    def success(cls, data: T):
        return cls(is_success=True, data=data)

    @classmethod
    def failure(cls, error: str, status_code: Optional[int] = None):
        return cls(is_success=False, error=error, status_code=status_code)