from pydantic import BaseModel, HttpUrl, Field


class RecipeForList(BaseModel):
    caption: str = ""
    description: str = ""
    image_url: HttpUrl = "https://adefe.xyz/avatar.png"
    id: int = Field(0, ge=0)


class StepForUI(BaseModel):
    caption: str = ""
    description: str = ""
    image_url: HttpUrl = "https://adefe.xyz/avatar.png"
    id: int = Field(0, ge=0)


class RecipeForUI(BaseModel):
    caption: str = ""
    description: str = ""
    image_url: HttpUrl = "https://adefe.xyz/avatar.png"
    steps: list[StepForUI] = []
