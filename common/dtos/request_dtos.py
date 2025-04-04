from django.http import QueryDict
from pydantic import (
    BaseModel,
    Field,
)


class GetPreSignedURLRequest(BaseModel):
    file_name: str = Field(description='Defined file name')

    @classmethod
    def of(cls, request: QueryDict):
        return cls(
            file_name=request.get('file_name'),
        )


class UploadFileRequest(BaseModel):
    file_name: str = Field(description='File name')
    file_content: bytes = Field(description='File content in bytes')

    @classmethod
    def of(cls, file_name: str, file_content: bytes):
        return cls(
            file_name=file_name,
            file_content=file_content,
        )
