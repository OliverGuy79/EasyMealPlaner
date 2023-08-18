from models.recipe import *
import json


def ingredients_from_db(ingredients_dict) -> list[RecipeIngredient]:
    recipe_ingredients = []

    for ingredient in ingredients_dict:
        amount = (
            int(ingredient["measures"]["metric"]["amount"])
            if ingredient["measures"]["metric"]["amount"].is_integer()
            else ingredient["measures"]["metric"]["amount"]
        )
        if ingredient["measures"]["metric"]["unitLong"] == "":
            ingredients_name = f"{amount} {ingredient['measures']['metric']['unitLong']} {ingredient['nameClean']}"
        else:
            ingredients_name = f"{amount} {ingredient['measures']['metric']['unitLong']} of {ingredient['nameClean']}"

        recipe_ingredients.append(
            RecipeIngredient(
                id=ingredient["id"],
                name=ingredients_name,
                aisle=ingredient["aisle"],
                amount=ingredient["measures"]["metric"]["amount"],
                unit_short=ingredient["measures"]["metric"]["unitShort"],
                unit_long=ingredient["measures"]["metric"]["unitLong"],
                original_string=ingredient["originalName"],
                image=ingredient["image"],
                meta_information=ingredient["meta"],
            )
        )
    return recipe_ingredients


def instructions_from_db(instructions_dict) -> list[RecipeInstruction]:
    instructions = []
    for instruction_step in instructions_dict[0]["steps"]:
        ingredients = []
        for ingredient in instruction_step["ingredients"]:
            ingredients.append(ingredient["id"])
        equipment = []
        for equipment_item in instruction_step["equipment"]:
            equipment.append(equipment_item["id"])
        instructions.append(
            RecipeInstruction(
                instruction=instruction_step["step"],
                ingredients=ingredients,
                equipment=equipment,
                duration=instruction_step["length"]["number"]
                if "length" in instruction_step
                else None,
            )
        )
    return instructions
