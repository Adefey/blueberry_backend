from pydantic import BaseModel, Field


class RecipeForList(BaseModel):
    caption: str = "Recipe name"
    description: str = "Recipe description"
    image_url: str = "https://adefe.xyz/avatar.png"
    id: int = Field(0, ge=0)


class RecipeList(BaseModel):
    recipes: list[RecipeForList] = []
    total: int = Field(0, ge=0)


class StepForUI(BaseModel):
    caption: str = "Step name"
    description: str = "Step description"
    image_url: str = "https://adefe.xyz/avatar.png"
    duration: int = Field(0, ge=0)


class RecipeForUI(RecipeForList):
    steps: list[StepForUI] = [
        StepForUI(caption="Step one"),
        StepForUI(caption="Step two"),
    ]
