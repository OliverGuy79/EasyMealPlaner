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

    if not table_service.exists("spoonacularUpdate"):
        table_service.create_table("spoonacularUpdate")
        table_service.insert_or_replace_entity(
            "spoonacularUpdate",
            Entity(PartitionKey="offset", RowKey="offset", Offset=str(0)),
        )
    try:
        offset = int(
            table_service.get_entity("spoonacularUpdate", "offset", "offset").Offset
        )
    except:
        offset = 0
        table_service.insert_or_replace_entity(
            "spoonacularUpdate",
            Entity(PartitionKey="offset", RowKey="offset", Offset=str(offset)),
        )


    with psycopg2.connect(
        host=os.environ["POSTGRES_HOST"],
        database="diet_on_budget",
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    ) as conn:
        with conn.cursor() as cursor:
            conn.autocommit = True
            cursor.execute(
                "select id, spoonacular_id, ingredients from spoonacular_recipe where id > %s limit 100",
                (offset,),
            )

            saved_recipes = cursor.fetchall()
            for saved_recipe in saved_recipes:
                logging.info(saved_recipe)
                if saved_recipe[2] is None:
                    #if saved_recipe[2] == recipe["ingredients"]:
                    url = f"https://api.spoonacular.com/recipes/{saved_recipe[1]}/information?includeNutrition=false&apiKey={os.environ['SPOONACULAR_API_KEY']}"
                    response = requests.get(url)
                    data = response.json()
                    ingredients = data["extendedIngredients"]
                    cursor.execute(
                        "UPDATE spoonacular_recipe SET ingredients = %s WHERE id = %s",
                        (json.dumps(ingredients), saved_recipe[0]),
                    )
                    continue

    offset += 100
    table_service.update_entity(
        "spoonacularUpdate",
        Entity(PartitionKey="offset", RowKey="offset", Offset=str(offset)),
    )

    if mytimer.past_due:
        logging.info("The timer is past due!")

    logging.info("Python timer trigger function ran at %s", utc_timestamp)
