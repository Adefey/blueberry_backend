from pydantic import BaseModel, Field, HttpUrl


class RecipeForList(BaseModel):
    caption: str = Field("Recipe name", min_length=2)
    description: str = Field("Recipe description", min_length=2)
    image_url: HttpUrl = Field("https://adefe.xyz/avatar.png", min_length=7)
    id: int = Field(0, ge=0)


class RecipeList(BaseModel):
    recipes: list[RecipeForList] = []
    total: int = Field(0, ge=0)


class StepForUI(BaseModel):
    caption: str = Field("Recipe name", min_length=2)
    description: str = Field("Recipe description", min_length=2)
    image_url: HttpUrl = Field("https://adefe.xyz/avatar.png", min_length=7)
    duration: int = Field(0, ge=0)


class RecipeForUI(RecipeForList):
    steps: list[StepForUI] = [
        StepForUI(caption="Step one"),
        StepForUI(caption="Step two"),
    ]
