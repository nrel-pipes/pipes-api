from pydantic import BaseModel, Field


class HPCStorage(BaseModel):
    """NREL HPC Storage Schema"""

    path: str = Field(
        title="path",
        description="The directory or file path on HPC storage.",
    )
    description: str | None = Field(
        title="description",
        default="",
        description="Description about this data path",
    )
