from fastapi import HTTPException
from pydantic import BaseModel, ValidationError
from typing import TypeVar

ModelT = TypeVar("ModelT", bound=BaseModel)


class ResponseValidationService:
    def validate_model(self, value: object, model_type: type[ModelT]) -> ModelT:
        try:
            if isinstance(value, model_type):
                return value
            return model_type.model_validate(value)
        except ValidationError as exc:
            raise HTTPException(status_code=502, detail="AI response did not match the expected schema.") from exc

    def ensure_grounded_answer(self, answer: str) -> str:
        if not answer.strip():
            raise HTTPException(status_code=502, detail="AI returned an empty response.")
        return answer.strip()


response_validator = ResponseValidationService()
