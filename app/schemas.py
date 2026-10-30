from pydantic import BaseModel, ConfigDict, Field


class IngredientCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    category: str = Field(min_length=1, max_length=80)
    unit: str = Field(min_length=1, max_length=30)


class IngredientRead(IngredientCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class RecipeIngredientCreate(IngredientCreate):
    amount: float = Field(gt=0)


class RecipeCreate(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    category: str = Field(min_length=1, max_length=80)
    preparation_minutes: int = Field(gt=0, le=1440)
    cooking_method: str = Field(min_length=1, max_length=80)
    servings: int = Field(gt=0, le=100)
    ingredients: list[RecipeIngredientCreate] = Field(min_length=1)
    steps: list[str] = Field(min_length=1)


class RecipeIngredientRead(BaseModel):
    amount: float
    ingredient: IngredientRead


class RecipeStepRead(BaseModel):
    position: int
    instruction: str


class RecipeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    category: str
    preparation_minutes: int
    cooking_method: str
    servings: int
    ingredients: list[RecipeIngredientRead]
    steps: list[RecipeStepRead]
