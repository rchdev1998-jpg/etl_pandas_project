import pandas as pd
import uuid
from connection import source_engine, target_engine
from metadata import tables_configuration
from logger import logger, save_etl_control
from datetime import datetime
from sqlalchemy import text


# GET THE LATEST END_ID PER TABLE INGESTED ===================================
def get_last_id(target_engine, table_name):

    query = f"""
            select 
            top 1 end_id 
            from etl_control 
            where table_name = '{table_name}' and status = 'SUCCESS' and table_schema = 'silver'
            order by completed_at DESC
            """
    df = pd.read_sql(
        query,
        target_engine
    )
    if df.empty:
        return None

    return df["end_id"].iloc[0]


# LOAD TO SILVER ==============================================================
def load_silver(chunk, table_name, schema, target_engine, chunk_no, total_rows):
    try:
        chunk.to_sql(
            name=table_name,
            con=target_engine,
            schema=schema,
            if_exists="append",
            index=False
        )

    except Exception as e:
        logger.exception(
            f"Process: LOAD | Status: Failed | Table name: {table_name} | Chunk: {chunk_no} | total_rows: {total_rows}")
        raise
# LOAD TO SILVER ==============================================================


# CLEANSE/TRANSFORMATION FUNCTIONS ===================================================
def cleanse_data(df):
    df = df.drop_duplicates()
    df.columns = df.columns.str.strip()
    return df


def cleanse_remove_null_strip_lower(table_name, df):
    df[f"{table_name}"] = df[f"{table_name}"].fillna(
        "n/a").str.strip().str.lower()
    return df


def transform_iwItems(df):
    itemgroup_mapping = {
        'PRC': 'procedure',
        'OTH': 'others',
        'MED': 'medicine',
        'EQP': 'equipment',
        'EXM': 'examination',
        'SUP': 'supplies'
    }

    df = cleanse_data(df)
    df = df.drop(columns=["barcodeid"])
    df["itemdesc"] = df["itemdesc"].str.strip().str.lower()
    df["itemgroup"] = df["itemgroup"].map(itemgroup_mapping)
    return df


def transform_mscWarehouse(df):
    df = cleanse_data(df)
    df["description"] = df["description"].str.strip().str.lower()
    return df


def transform_psPatitem(df):
    df = cleanse_data(df)
    return df


def transform_psPatRegisters(df):
    pattrantype_mapping = {
        'I': 'inpatient',
        'O': 'outpatient',
        'E': 'emergency'
    }

    registry_status_mapping = {
        'N': 'billing discharge',
        'A': 'active',
        'X': 'cancel',
        'D': 'discharge',
        'F': 'for mgh clearance',
        'U': 'untag mgh',
        'C': 'cleared / can be tag as mgh',
        'M': 'mgh',
        'B': 'clinical discharge'
    }
    df["pattrantype"] = df["pattrantype"].map(pattrantype_mapping)
    df["registrystatus"] = df["registrystatus"].map(registry_status_mapping)
    return df
# END OF TRANSFORMATION =================================================


def transform_psPersonaldata(df):
    df = cleanse_data(df)
    df = cleanse_remove_null_strip_lower("firstname", df)
    df = cleanse_remove_null_strip_lower("gender", df)
    df = cleanse_remove_null_strip_lower("religion", df)
    df = cleanse_remove_null_strip_lower("nationality", df)
    return df


# TRANSFORM FUNCTIONS ===================================================
def transform_data(table_name, chunk, chunk_no, total_rows):
    try:
        match table_name:
            case 'iwItems':
                transformed = transform_iwItems(chunk)
            case 'mscWarehouse':
                transformed = transform_mscWarehouse(chunk)
            case 'psPatitem':
                transformed = transform_psPatitem(chunk)
            case 'psPatRegisters':
                transformed = transform_psPatRegisters(chunk)
            case 'psPersonaldata':
                transformed = transform_psPersonaldata(chunk)

        return transformed

    except Exception as e:
        logger.exception(
            f"Process: TRANSFORM | Status: Failed | Table name: {table_name} | Chunk: {chunk_no} | Total rows: {total_rows}")
        raise
# CLEANSE/TRANSFORMATION FUNCTIONS ===================================================


# EXTRACT FUNCTIONS ===================================================
def extract_data(target_engine, table_name, key_column, column_type, last_id):
    try:

        # =====================================================
        # INITIAL LOAD
        # =====================================================
        if last_id is None:

            query = text(f"""
                SELECT *
                FROM bronze.{table_name} 
                ORDER BY {key_column}
            """)

            chunks = pd.read_sql(
                query,
                target_engine,
                chunksize=10_000
            )

        # =====================================================
        # INCREMENTAL LOAD
        # =====================================================
        else:

            if column_type == "int":
                last_id = int(last_id)

            query = text(f"""
                SELECT *
                FROM bronze.{table_name}
                WHERE {key_column} > :last_id
                ORDER BY {key_column}
            """)

            chunks = pd.read_sql(
                query,
                target_engine,
                params={"last_id": last_id},
                chunksize=10_000
            )

        # =====================================================
        # PROCESS CHUNKS
        # =====================================================
        for chunk_no, chunk in enumerate(chunks, start=1):

            # Important: don't process empty chunks
            if chunk.empty:
                continue

            start_id = chunk[key_column].iloc[0]
            end_id = chunk[key_column].iloc[-1]

            yield chunk_no, start_id, end_id, chunk

    except Exception:
        logger.exception(
            f"Process: Extract | Status: Failed | Table name: {table_name}"
        )
        raise

# EXTRACT FUNCTIONS ===================================================


def silver_process():
    # =====================================================
    # SILVER PROCESS
    # 1. Extract the data from bronze layer
    # 2. TRANSFORM
    # 3. LOAD to silver cleaned and transformed data
    # =====================================================
    target = target_engine()
    tables = tables_configuration()

    # One Batch ID for the entire pipeline execution
    batch_id = datetime.now().strftime("%Y%m%d%H%M%S")

    logger.info("========== SILVER LAYER ==========")

    for table, configuration in tables.items():

        started_at = datetime.now()
        chunk_no = 0
        total_rows = 0
        run_id = str(uuid.uuid4())
        last_id = get_last_id(target, table)
        first_start_id = None
        last_end_id = None
        has_data = False

        try:

            # ===============================================
            # EXTRACT
            # ===============================================
            chunked = extract_data(
                target,
                table,
                configuration["column_key"],
                configuration["column_type"],
                last_id
            )

            # ===============================================
            # TRANSFORM + LOAD
            # ===============================================
            for chunk_no, start_id, end_id, chunk in chunked:

                has_data = True
                if first_start_id is None:
                    first_start_id = start_id

                last_end_id = end_id

                started_at = datetime.now()
                chunk_rows = len(chunk)
                total_rows += chunk_rows

                try:
                    # ===============================================
                    # TRANSFORM
                    # ===============================================
                    transformed_data = transform_data(
                        table, chunk, chunk_no, total_rows)

                    # ===============================================
                    # LOAD
                    # ===============================================
                    load_silver(
                        transformed_data, table, "silver", target, chunk_no, total_rows)

                    # ===============================================
                    # LOG
                    # ===============================================
                    completed_at = datetime.now()
                    save_etl_control(
                        target, batch_id, run_id, "silver", table, chunk_no, start_id, end_id, len(chunk), "SUCCESS", started_at, completed_at)

                except Exception as e:

                    completed_at = datetime.now()
                    save_etl_control(
                        target, batch_id, run_id, "silver", table, chunk_no, start_id, end_id, len(chunk), "FAILED", started_at, completed_at, str(e))
                    raise
            # =====================================================
            # NO DATA
            # =====================================================
            completed_at = datetime.now()
            if not has_data:

                if last_id is None:
                    logger.info(
                        f"Process: Extract | Table: {table} | "
                        f"No records found in source table"
                    )

                    save_etl_control(
                        target, batch_id, run_id, "silver", table, 0, last_id, last_id, 0, "NO DATA", started_at, completed_at, "No records found in source table")

                else:
                    logger.info(
                        f"Process: Extract | Table: {table} | "
                        f"No new records found | Last ID: {last_id}"
                    )

                    save_etl_control(
                        target, batch_id, run_id, "silver", table, 0, None, None, 0, "NO DATA", started_at, completed_at, "No new records found in source table")

            else:

                logger.info(
                    f"LAYER: SILVER | Table name: {table} | Total Chunk: {chunk_no} | Total rows: {total_rows} | Start ID: {first_start_id} | Last ID: {last_end_id} | STATUS: SUCCESS")

        except Exception:

            logger.info(
                f"LAYER: SILVER | Table name: {table} | Total Chunk: {chunk_no} | Total rows: {total_rows} | Start ID: {first_start_id} | Last ID: {last_end_id} | STATUS: FAILED")
            raise
