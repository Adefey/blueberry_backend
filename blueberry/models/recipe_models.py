from pydantic import BaseModel, Field


class RecipeForList(BaseModel):
    caption: str = ""
    description: str = ""
    image_url: str = "https://adefe.xyz/avatar.png"
    id: int = Field(0, ge=0)


class RecipeList(BaseModel):
    recipes: list[RecipeForList]


class StepForUI(BaseModel):
    caption: str = "Step name"
    description: str = "Step description"
    image_url: str = "https://adefe.xyz/avatar.png"
    duration: int = Field(0, ge=0)


class RecipeForUI(RecipeForList):
    steps: list[StepForUI] = [StepForUI]
