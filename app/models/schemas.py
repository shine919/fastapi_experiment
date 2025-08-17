import re
from fastapi import HTTPException
from pydantic import BaseModel, field_validator, model_validator

from core.config import settings


class Item(BaseModel):
    name: str



def check_pattern(string:str,pattern:str = None):
    if pattern is None:
        pattern = r'[a-z]{2}-[A-Z]{2},[a-z]{2};q=\w\.\w,[a-z]{2};q=\w\.\w'
    result = re.findall(pattern, string)
    return result


def check_version(
        version_request: str
        ) -> str | bool:
    if '"' in version_request or "'" in version_request:
        version = version_request[1:-1]
    else:
        version = version_request
    def parse_version(
            ver: str
            ) -> list[int]:

        parts = list(map(int, ver.split('.')))
        parts += [0] * (3 - len(parts))
        return parts[:3]

    req = parse_version(version)
    res = parse_version(settings.version)


    for req_part, res_part in zip(req, res):
        if req_part > res_part:
            return version
        elif req_part < res_part:
            return False
    return version


class CommonHeaders(BaseModel):
    user_agent: str
    accept_language: str
    x_current_version: str

    @model_validator(mode="after")
    def validate_accept_language(self):
        if self.accept_language is not None:
            if not check_pattern(self.accept_language):
                raise HTTPException(status_code=400, detail="Accept Language is invalid")
        return self
    @field_validator("x_current_version",mode="before")
    def validate_x_current_version(cls,version):
        if version is not None:
            pattern = r'\d+[.]\d+[.]\d+'
            if not check_pattern(version,pattern):
                raise HTTPException(status_code=400, detail="Current Version is invalid")
            if not (cleaned_version:=check_version(version)):
                raise HTTPException(status_code=422,detail = "Требуется обновить приложение")
            return cleaned_version
        raise HTTPException(status_code=400, detail="X-Current-Version is invalid")



# class UserAgeResponse(User):
#     @computed_field
#     @property
#     async def is_adult(self)->bool:
#         return self.age >= 18

# class Feedback(BaseModel):
#     name : str = Field(min_length=2, max_length=50)
#     message : str = Field(min_length=10, max_length=500)
#     contact : Contact
#
#     @field_validator("message",mode='before')
#     def validate_message(cls,value):
#         forbidden_words = ["редиска", "бяка", "козявка"]
#         pattern = r'\b(?:' + '|'.join(w[:-1] for w in forbidden_words) + '(а|и|е|у|ой|ою)' + r')\w*\b'
#         for word in forbidden_words:
#             if re.search(pattern, value.lower()):
#                 raise ValueError(f"Слово '{word}' запрещено в поле message")
#
#
#         return value
#
