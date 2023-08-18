import logging
import psycopg2
import azure.functions as func
from models.recipe import *
from models.model_builder import *
from db import db_pool
from models.api_models import *
import uuid
import sys

_logger = logging.getLogger("meal_plan__init__")
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
_logger.addHandler(stream_handler)


def main(req: func.HttpRequest) -> func.HttpResponse:
    _logger.info("Python HTTP trigger function processed a request.")

    if req.method == "GET":
        meal_plan_id = req.params.get("mealPlanId")

    if req.method == "POST":
        try:
            request_body = GenerateMealPlanRequest(**req.get_json())
        except ValueError:
            return func.HttpResponse("Invalid JSON Body", status_code=400)
        vegan = request_body.vegan
        vegetarian = request_body.vegetarian
        price_per_meal = request_body.price_per_meal
        _logger.info(f"{vegan}, {vegetarian}, {price_per_meal}")
        recipes = generate_meal_plan(price_per_meal, vegan, vegetarian)
        if recipes:
            #_logger.info(recipes)
            api_json_response = {"id": str(uuid.uuid4()), "recipes": recipes}
            save_meal_plan(recipes)
            return func.HttpResponse(
                json.dumps(api_json_response),
                status_code=200,
                headers={"Content-Length": len(json.dumps(api_json_response))},
            )
        return func.HttpResponse(json.dumps({"message": "error"}), status_code=422)


def save_meal_plan(recipes: list[Recipe]):
    _logger.info("save_meal_plan function processed a request.")
    if recipes is None or len(recipes) != 7:
        _logger.error("Error while saving meal plan. Invalid recipes list")
        _logger.error(f"recipe list length: {len(recipes)}")
        return False
    db_connection = db_pool.pg_connection_pool.getconn()
    if db_connection:
        cursor = db_connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO meal_plan (monday_meal_id, tuesday_meal_id, wednesday_meal_id, thursday_meal_id, friday_meal_id, saturday_meal_id, sunday_meal_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (
                    recipes[0]["id"],
                    recipes[1]["id"],
                    recipes[2]["id"],
                    recipes[3]["id"],
                    recipes[4]["id"],
                    recipes[5]["id"],
                    recipes[6]["id"],
                ),
            )
            db_connection.commit()
            return True
        except (Exception, psycopg2.DatabaseError) as error:
            _logger.error(error)
            db_connection.rollback()
            return False
        finally:
            db_pool.pg_connection_pool.putconn(db_connection)
            cursor.close()
    else:
        _logger.error("Error while connecting to PostgreSQL database")


def generate_meal_plan(price_per_meal: float, vegan: bool, vegeterian: bool):
    _logger.info("generate_meal_plan function processed a request.")

    db_connection = db_pool.pg_connection_pool.getconn()
    recipes = []
    if db_connection:
        cursor = db_connection.cursor()
        try:
            cursor.execute(
                "select * from spoonacular_recipe where price <= %s  and vegan = %s and vegeterian = %s and 'main course' = ANY(dish_types) and ingredients is not null ORDER BY RANDOM () limit 7",
                (
                    price_per_meal * 100,
                    vegan,
                    vegeterian,
                ),
            )

            saved_recipes = cursor.fetchall()
            if len(saved_recipes) == 0:
                _logger.error("No recipes found")
                return None
            elif len(saved_recipes) != 7:
                _logger.warning("Not enough recipes found")

            _logger.info(f"Recipes from the DB: \n{saved_recipes}")
            _logger.info(f"{len(saved_recipes)} found recipes")
            for saved_recipe in saved_recipes:
                recipes.append(
                    Recipe(
                        id=saved_recipe[0],
                        spoonacular_id=saved_recipe[1],
                        recipe_name=saved_recipe[2],
                        image_link=saved_recipe[3],
                        price=saved_recipe[7],
                        cuisine_type="",
                        vegetarian=saved_recipe[9],
                        vegan=saved_recipe[10],
                        prep_cook_time=saved_recipe[4],
                        servings=saved_recipe[5],
                        instructions=instructions_from_db(saved_recipe[13]),
                        ingredients=ingredients_from_db(saved_recipe[14]),
                    ).dict()
                )
                _logger.info(f"Recipe: {recipes[-1]}")
        except (Exception, psycopg2.DatabaseError) as error:
            _logger.error(f"Error while generating meal plan from recipe database. {error}")
            _logger.error(f"{error.__str__()}")
        cursor.close()
        # Use this method to release the connection object and send back to connection pool
        db_pool.pg_connection_pool.putconn(db_connection)
        return recipes
    return None


def find_meal_plan(meal_plan_id: int):
    _logger.info("find_meal_plan function processed a request.")

    db_connection = db_pool.pg_connection_pool.getconn()
    recipes = []
    if db_connection:
        cursor = db_connection.cursor()
        try:
            cursor.execute(
                "select * from meal_plan where id = %s",
                (meal_plan_id,),
            )

            meal_plan = cursor.fetchone()
            if meal_plan is None:
                _logger.info("No meal plan found")
                return None
            _logger.info(f"{meal_plan} found meal plan")

            cursor.execute(
                "select * from spoonacular_recipe where id = ANY(%s)",
                (
                    [
                        meal_plan[1],
                        meal_plan_id[2],
                        meal_plan_id[3],
                        meal_plan_id[4],
                        meal_plan_id[5],
                        meal_plan_id[6],
                        meal_plan_id[7],
                    ]
                ),
            )

            saved_recipes = cursor.fetchall()

            if len(saved_recipes) == 0:
                _logger.info("No recipes found")
                return None

            _logger.info(f"{len(saved_recipes)} found recipes")
            for saved_recipe in saved_recipes:
                recipes.append(
                    Recipe(
                        id=saved_recipe[0],
                        spoonacular_id=saved_recipe[1],
                        recipe_name=saved_recipe[2],
                        image_link=saved_recipe[3],
                        price=saved_recipe[7],
                        cuisine_type="",
                        vegetarian=saved_recipe[9],
                        vegan=saved_recipe[10],
                        prep_cook_time=saved_recipe[4],
                        servings=saved_recipe[5],
                        instructions=instructions_from_db(saved_recipe[13]),
                        ingredients=ingredients_from_db(saved_recipe[14]),
                    ).dict()
                )
        except (Exception, psycopg2.DatabaseError) as error:
            _logger.error(f"Database Error .Recipe id: {saved_recipe[0]}")
            _logger.error(error)
        cursor.close()
        # Use this method to release the connection object and send back to connection pool
        db_pool.pg_connection_pool.putconn(db_connection)
        return recipes
    return None
