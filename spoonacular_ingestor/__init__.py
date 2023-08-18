import datetime
import logging
import json
import os
import psycopg2
import requests

from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity

import azure.functions as func


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = (
        datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    )

    table_service = TableService(
        account_name=os.environ["AZURE_STORAGE_ACCOUNT"],
        account_key=os.environ["AZURE_STORAGE_KEY"],
    )

    try:
        offset = int(table_service.get_entity("spoonacular", "offset", "offset").Offset)
    except:
        offset = 0
        table_service.insert_or_replace_entity(
            "spoonacular",
            Entity(PartitionKey="offset", RowKey="offset", Offset=str(offset)),
        )

    offset = int(table_service.get_entity("spoonacular", "offset", "offset").Offset)
    url = f"https://api.spoonacular.com/recipes/complexSearch?offset={offset}&number=100&apiKey={os.environ['SPOONACULAR_API_KEY']}&addRecipeInformation=true&fillIngredients=true"
    response = requests.get(url)
    data = response.json()
    recipes = data["results"]
    test1 = json.dumps(recipes[0]["analyzedInstructions"][0]["steps"])

    conn = psycopg2.connect(
        host=os.environ["POSTGRES_HOST"],
        database="diet_on_budget",
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )
    cursor = conn.cursor()
    for recipe in recipes:
        cursor.execute(
            "INSERT INTO spoonacular_recipe_1 (spoonacular_id, title, image, ready_in_minutes, servings, source_url, price, summary, vegeterian, vegan, cheap, dish_types, instructions, ingredients) VALUES (%s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s)",
            (
                recipe["id"],
                recipe["title"],
                recipe["image"],
                recipe["readyInMinutes"],
                recipe["servings"],
                recipe["sourceUrl"],
                recipe["pricePerServing"] * recipe["servings"],
                recipe["summary"],
                recipe["vegetarian"],
                recipe["vegan"],
                recipe["cheap"],
                recipe["dishTypes"],
                json.dumps(recipe["analyzedInstructions"]),
                json.dumps(recipe["extendedIngredients"]),
            ),
        )
    conn.commit()
    cursor.close()
    conn.close()

    offset += data["number"]
    table_service.update_entity(
        "spoonacular",
        Entity(PartitionKey="offset", RowKey="offset", Offset=str(offset)),
    )

    if mytimer.past_due:
        logging.info("The timer is past due!")

    logging.info("Python timer trigger function ran at %s", utc_timestamp)
