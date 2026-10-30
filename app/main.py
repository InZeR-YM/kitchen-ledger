from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from . import models
from .database import Base, SessionLocal, engine, get_db
from .models import Ingredient, Recipe
from .schemas import IngredientCreate, IngredientRead, RecipeCreate, RecipeRead
from .services import RecipeService


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if db.scalar(select(func.count()).select_from(Recipe)) == 0:
            RecipeService.create(db, RecipeCreate(
                title="Овощной суп",
                category="Супы",
                preparation_minutes=35,
                cooking_method="варка",
                servings=4,
                ingredients=[
                    {"name": "Картофель", "category": "Овощи", "unit": "г", "amount": 300},
                    {"name": "Морковь", "category": "Овощи", "unit": "шт.", "amount": 1},
                    {"name": "Соль", "category": "Специи", "unit": "ч.л.", "amount": 1},
                ],
                steps=["Нарежьте картофель и морковь.", "Залейте водой и варите до мягкости.", "Посолите и подавайте горячим."],
            ))
    yield


app = FastAPI(title="Kitchen Ledger API", version="1.0.0", lifespan=lifespan)
WEB_DIR = Path(__file__).parent / "web"


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(WEB_DIR / "index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ingredients", response_model=IngredientRead, status_code=201)
def create_ingredient(data: IngredientCreate, db: Session = Depends(get_db)):
    existing = db.scalar(select(Ingredient).where(Ingredient.name.ilike(data.name)))
    if existing:
        raise HTTPException(status_code=409, detail="Ингредиент с таким названием уже существует")
    ingredient = Ingredient(**data.model_dump())
    db.add(ingredient)
    db.commit()
    db.refresh(ingredient)
    return ingredient


@app.get("/ingredients", response_model=list[IngredientRead])
def list_ingredients(db: Session = Depends(get_db)):
    return list(db.scalars(select(Ingredient).order_by(Ingredient.name)).all())


@app.post("/recipes", response_model=RecipeRead, status_code=201)
def create_recipe(data: RecipeCreate, db: Session = Depends(get_db)):
    try:
        return RecipeService.create(db, data)
    except Exception:
        db.rollback()
        raise


@app.get("/recipes", response_model=list[RecipeRead])
def search_recipes(
    q: str | None = None,
    category: str | None = None,
    method: str | None = None,
    max_minutes: int | None = Query(default=None, gt=0),
    ingredients: str | None = Query(default=None, description="Названия через запятую; требуются все указанные"),
    db: Session = Depends(get_db),
):
    names = ingredients.split(",") if ingredients else None
    return RecipeService.search(db, q, category, method, max_minutes, names)


@app.get("/recipes/{recipe_id}", response_model=RecipeRead)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    recipe = db.get(Recipe, recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail="Рецепт не найден")
    return recipe
