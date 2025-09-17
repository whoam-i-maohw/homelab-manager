from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class NutritionBreakdown:
    summary: str
    calories: str
    protein: str
    carbohydrates: str
    fiber: str
    fats: str
    saturated_fat: str
    sodium: str
    sugar: str
