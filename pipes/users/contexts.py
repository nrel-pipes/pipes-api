from pydantic import BaseModel, Field

from pipes.users.schemas import UserDocument


class UserContext(BaseModel):
    user: UserDocument | None = Field(
        title="user",
        default=None,
        description="current user",
    )
