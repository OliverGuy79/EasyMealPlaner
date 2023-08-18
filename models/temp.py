import json
import psycopg2


with psycopg2.connect(
    host='parkingfinderdb.postgres.database.azure.com',
    database="diet_on_budget",
    user='oliver',
    password='Eliane81',
) as conn:
    with conn.cursor() as cursor:
        conn.autocommit = True
        cursor.execute(
            "select * from spoonacular_recipe where price <= %s limit 100",
            (10*100,),
        )

        saved_recipes = cursor.fetchall()
        print(saved_recipes[0][12])
#        for saved_recipe in saved_recipes:
