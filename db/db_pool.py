import psycopg2
import psycopg2.pool
import os
import logging


try:
    # Create a connection pool
    pg_connection_pool = psycopg2.pool.SimpleConnectionPool(
        1, # minimum number of connections
        20, # maximum number of connections
        host=os.environ["POSTGRES_HOST"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        dbname="diet_on_budget"
    )
except Exception as e:
    logging.error("Exception while connecting to PostgresSQL", e)
    pg_connection_pool = None