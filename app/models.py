from sqlalchemy import ForeignKey, String, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    category: Mapped[str] = mapped_column(String(80), index=True)
    unit: Mapped[str] = mapped_column(String(30))


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(160), index=True)
    category: Mapped[str] = mapped_column(String(80), index=True)
    preparation_minutes: Mapped[int] = mapped_column(Integer)
    cooking_method: Mapped[str] = mapped_column(String(80), index=True)
    servings: Mapped[int] = mapped_column(Integer)
    ingredients: Mapped[list["RecipeIngredient"]] = relationship(
        back_populates="recipe", cascade="all, delete-orphan", lazy="selectin"
    )
    steps: Mapped[list["RecipeStep"]] = relationship(
        back_populates="recipe", cascade="all, delete-orphan", order_by="RecipeStep.position", lazy="selectin"
    )


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"

    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"), primary_key=True)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id"), primary_key=True)
    amount: Mapped[float] = mapped_column(Float)
    recipe: Mapped[Recipe] = relationship(back_populates="ingredients")
    ingredient: Mapped[Ingredient] = relationship(lazy="joined")


class RecipeStep(Base):
    __tablename__ = "recipe_steps"

    id: Mapped[int] = mapped_column(primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"), index=True)
    position: Mapped[int] = mapped_column(Integer)
    instruction: Mapped[str] = mapped_column(String(500))
    recipe: Mapped[Recipe] = relationship(back_populates="steps")
