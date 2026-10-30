from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models import Ingredient, Recipe, RecipeIngredient, RecipeStep
from .schemas import RecipeCreate


class RecipeService:
    @staticmethod
    def create(db: Session, data: RecipeCreate) -> Recipe:
        recipe = Recipe(
            title=data.title,
            category=data.category,
            preparation_minutes=data.preparation_minutes,
            cooking_method=data.cooking_method,
            servings=data.servings,
        )
        for item in data.ingredients:
            ingredient = db.scalar(select(Ingredient).where(func.lower(Ingredient.name) == item.name.lower()))
            if ingredient is None:
                ingredient = Ingredient(name=item.name, category=item.category, unit=item.unit)
            recipe.ingredients.append(RecipeIngredient(ingredient=ingredient, amount=item.amount))
        recipe.steps = [RecipeStep(position=index, instruction=step) for index, step in enumerate(data.steps, 1)]
        db.add(recipe)
        db.commit()
        db.refresh(recipe)
        return recipe

    @staticmethod
    def search(db: Session, q: str | None, category: str | None, method: str | None,
               max_minutes: int | None, ingredients: list[str] | None) -> list[Recipe]:
        stmt = select(Recipe).distinct()
        if q:
            stmt = stmt.where(Recipe.title.ilike(f"%{q}%"))
        if category:
            stmt = stmt.where(func.lower(Recipe.category) == category.lower())
        if method:
            stmt = stmt.where(func.lower(Recipe.cooking_method) == method.lower())
        if max_minutes is not None:
            stmt = stmt.where(Recipe.preparation_minutes <= max_minutes)
        if ingredients:
            normalized = [name.strip().lower() for name in ingredients if name.strip()]
            if normalized:
                stmt = stmt.join(Recipe.ingredients).join(RecipeIngredient.ingredient)
                stmt = stmt.where(func.lower(Ingredient.name).in_(normalized))
                stmt = stmt.group_by(Recipe.id).having(func.count(func.distinct(Ingredient.id)) == len(set(normalized)))
        return list(db.scalars(stmt.order_by(Recipe.title)).unique().all())
