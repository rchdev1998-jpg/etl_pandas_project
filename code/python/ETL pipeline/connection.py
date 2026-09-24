import os
import urllib.parse
from sqlalchemy import create_engine, text
from logger import logger


driver = "ODBC Driver 18 for Sql Server"


def source_connection():
    # ENVIRONMENT VARIABLES
    server_name = os.getenv("ETL_SOURCE_SERVER")
    database = os.getenv("ETL_SOURCE_DATABASE")
    uid = os.getenv("ETL_DB_USER")
    pwd = os.getenv("ETL_DB_PASSWORD")

    connection_string = (
        f"DRIVER={{{driver}}};"
        f"SERVER={server_name};"
        f"DATABASE={database};"
        f"UID={uid};"
        f"PWD={pwd};"
        "TrustServerCertificate=yes;"
    )
    return connection_string


def source_engine():
    connection_params = urllib.parse.quote_plus(source_connection())
    engine = create_engine(
        f"mssql+pyodbc:///?odbc_connect={connection_params}")
    try:
        with engine.connect() as connection:
            connection.execute(text("select 1"))
        logger.info("===PROCESS: Source Connection | STATUS: Success===")
        return engine
    except Exception as e:
        logger.exception("===PROCESS: Source Connection | STATUS: Failed===")
        raise


def target_connection():
    target_connection_string = (
        f"DRIVER={{{driver}}};"
        "SERVER=RCH-FACILITY1;"
        "DATABASE=DATA_WAREHOUSE;"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )
    return target_connection_string


def target_engine():
    connection_params = urllib.parse.quote_plus(target_connection())
    engine = create_engine(
        f"mssql+pyodbc:///?odbc_connect={connection_params}")
    try:
        with engine.connect() as connection:
            connection.execute(text("select 1"))
            logger.info("===PROCESS: Target Connection | STATUS: Success")
        return engine
    except Exception as e:
        logger.exception("===PROCESS: Target Connection | STATUS: Failed")
        raise
