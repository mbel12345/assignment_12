from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field

class TokenType(str, Enum):

    # Valid token types

    ACCESS = 'access'
    REFRESH = 'refresh'

class Token(BaseModel):

    access_token: str = Field(..., description='JWT access token')
    refresh_token: str = Field(..., description='JWT refresh token')
    token_type: str = Field(default='bearer', description='Token type')
    expires_at: datetime = Field(..., description='Token expiration timestamp')

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
           "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "bearer",
                "expires_at": "2025-01-01T00:00:00"
            }
        }
    )
