from pydantic import BaseModel, Field


class AmazonS3Schema(BaseModel):
    """Amazon S3 Location Schema"""

    system: str = Field(
        title="system",
        default="AmazonS3",
        description="Data system of the location",
    )
    bucket: str = Field(
        title="bucket",
        description="AWS bucket name",
    )
    keys: list[str] = Field(
        title="keys",
        default=[],
        description="List of keys to retrieve",
    )
    description: str = Field(
        title="description",
        default="",
        description="Description of this location",
    )
