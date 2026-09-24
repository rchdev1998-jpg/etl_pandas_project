import pandas as pd
import uuid
from connection import source_engine, target_engine
from metadata import tables_configuration
from logger import logger, save_etl_control
from datetime import datetime
from sqlalchemy import text


def get_last_id(target_engine, table_name):

    query = text("""
        SELECT TOP 1 end_id
        FROM etl_control
        WHERE table_name = :table_name
          AND status = 'SUCCESS'
          AND table_schema = 'bronze'
        ORDER BY completed_at DESC
    """)

    df = pd.read_sql(
        query,
        target_engine,
        params={"table_name": table_name}
    )

    if df.empty:
        return None

    return df["end_id"].iloc[0]


# LOAD TO BRONZE LAYER ===================================================================
def load_data(chunk, table_name, target_engine, schema, chunk_no, total_rows):

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


# EXTRACT FROM DATA SOURCE SQL SERVER =======================================================
def extract_bronze(query, source_engine, table_name, chunk_no, total_rows, last_id, key_column):

    try:

        match table_name:
            case "iwItems":
                source_query = text(
                    "select PK_iwItems, barcodeid, itemdesc, itemgroup from dbo.iwItems WHERE PK_iwItems > :last_id order by PK_iwItems")
            case "mscWarehouse":
                source_query = text(
                    "select PK_mscWarehouse, description from dbo.mscWarehouse where PK_mscWarehouse > :last_id  order by PK_mscWarehouse")
            case "psPatitem":
                source_query = text("select PK_psPatitem, FK_psPatRegisters, FK_emdPatients, FK_mscWarehouse, FK_iwItemsREN, renqty, renprice, rendate from dbo.psPatitem where rendate >= '2020-01-01' and rendate < '2021-01-01' and PK_psPatitem > :last_id order by PK_psPatitem")
            case "psPatRegisters":
                source_query = text("select PK_psPatRegisters, FK_emdPatients, registrydate, dischdate, pattrantype, registrystatus, cancelflag from dbo.psPatRegisters where registrydate >= '2020-01-01' and registrydate < '2021-01-01' and PK_psPatRegisters > :last_id order by PK_psPatRegisters")
            case "psPersonaldata":
                source_query = text(
                    "select PK_psPersonalData, firstname, gender, religion, nationality from dbo.psPersonaldata where PK_psPersonalData > :last_id order by PK_psPersonalData")

        # =====================================================
        # INITIAL EXTRACTION
        # =====================================================
        if last_id is None:
            chunks = pd.read_sql(
                query,
                source_engine,
                chunksize=10_000
            )

        # =====================================================
        # INCREMENTAL EXTRACTION
        # =====================================================
        else:
            chunks = pd.read_sql(
                source_query,
                source_engine,
                params={"last_id": last_id},
                chunksize=10_000
            )

        # =====================================================
        # PROCESS CHUNKS
        # =====================================================
        for chunk_no, chunk in enumerate(chunks, start=1):

            if chunk.empty:
                continue

            start_id = chunk[key_column].iloc[0]
            end_id = chunk[key_column].iloc[-1]

            yield chunk_no, start_id, end_id, chunk

    except Exception as e:
        logger.exception(
            f"Process: Extract | Status: Failed | Table name: {table_name} | Chunk: {chunk_no} | total_rows: {total_rows}")
        raise


# GET TOTAL ROWS COUNT FROM SOURCE DATA========================================
def get_source_count(table_name, engine, key_column, start_id, end_id):
    query = text(f"""
        SELECT COUNT(*)
        FROM dbo.{table_name}
        WHERE {key_column} BETWEEN :start_id AND :end_id
    """)

    with engine.connect() as connection:
        return connection.execute(
            query,
            {
                "start_id": start_id,
                "end_id": end_id
            }
        ).scalar_one()


def get_target_count(table_name, engine, key_column, start_id, end_id):
    query = text(f"""
        SELECT COUNT(*)
        FROM bronze.{table_name}
        WHERE {key_column} BETWEEN :start_id AND :end_id
    """)

    with engine.connect() as connection:
        return connection.execute(
            query,
            {
                "start_id": start_id,
                "end_id": end_id
            }
        ).scalar_one()


# DELETE INITIAL DATA========================================
def delete_initial_data(table_name, engine, key_column, start_id, end_id):

    query = text(f"""
        DELETE FROM bronze.{table_name}
        WHERE {key_column} BETWEEN :start_id AND :end_id
        """)

    with engine.begin() as connection:
        connection.execute(
            query,
            {
                "start_id": start_id,
                "end_id": end_id
            }
        )


def load_initial_data(table_name, target_engine, source_engine, target_schema, start_id, last_id):

    # CONTROL THE DATA TO EXTRACT ===================================
    match table_name:
        case "iwItems":
            source_query = text(
                "select PK_iwItems, barcodeid, itemdesc, itemgroup from dbo.iwItems WHERE PK_iwItems between :start_id and :last_id order by PK_iwItems")
        case "mscWarehouse":
            source_query = text(
                "select PK_mscWarehouse, description from dbo.mscWarehouse where PK_mscWarehouse between :start_id and :last_id  order by PK_mscWarehouse")
        case "psPatitem":
            source_query = text("select PK_psPatitem, FK_psPatRegisters, FK_emdPatients, FK_mscWarehouse, FK_iwItemsREN, renqty, renprice, rendate from dbo.psPatitem where rendate >= '2020-01-01' and rendate < '2021-01-01' and PK_psPatitem between :start_id and :last_id order by PK_psPatitem")
        case "psPatRegisters":
            source_query = text("select PK_psPatRegisters, FK_emdPatients, registrydate, dischdate, pattrantype, registrystatus, cancelflag from dbo.psPatRegisters where registrydate >= '2020-01-01' and registrydate < '2021-01-01' and PK_psPatRegisters between :start_id and :last_id order by PK_psPatRegisters")
        case "psPersonaldata":
            source_query = text(
                "select PK_psPersonalData, firstname, gender, religion, nationality from dbo.psPersonaldata where PK_psPersonalData between :start_id and :last_id order by PK_psPersonalData")

    # ========================================
    # EXTRACT THE INITIAL DATA
    # ========================================
    chunks = pd.read_sql(
        source_query,
        source_engine,
        params={"start_id": start_id, "last_id": last_id},
        chunksize=10_000
    )

    # ========================================
    # LOAD THE INITIAL DATA
    # ========================================
    for chunk in chunks:
        chunk.to_sql(
            name=table_name,
            con=target_engine,
            schema=target_schema,
            if_exists="append",
            index=False
        )


def bronze_process():
    # ===============================================================
    # Bronze layer
    # 1. Extract from data source SQL SERVER
    # 2. Load to bronze layer Data warehouse
    # ===============================================================
    source = source_engine()
    target = target_engine()
    tables = tables_configuration()
    max_attempt = 3

    # One Batch ID for the entire pipeline execution
    batch_id = datetime.now().strftime("%Y%m%d%H%M%S")

    logger.info("========== BRONZE LAYER ==========")

    for table, query in tables.items():

        started_at = datetime.now()
        total_rows = 0
        # Unique run_id for table execution. extract -> transform -> load
        run_id = str(uuid.uuid4())
        last_id = get_last_id(target, table)
        has_data = False
        first_start_id = None
        last_end_id = None
        chunk_no = 0

        try:

            # ================================================
            # EXTRACT
            # ================================================
            chunked = extract_bronze(
                query["target_query"], source, table, 0, 0, last_id, query["column_key"])

            for chunk_no, start_id, end_id, chunk in chunked:

                if first_start_id is None:
                    first_start_id = start_id

                last_end_id = end_id

                has_data = True
                chunk_rows = len(chunk)
                total_rows += chunk_rows

                try:

                    # ================================================
                    # LOAD
                    # ================================================
                    load_data(chunk, table, target,
                              "bronze", chunk_no, chunk_rows)

                    # ================================================
                    # LOG TO etl_control | SUCCESS
                    # ================================================
                    completed_at = datetime.now()

                    save_etl_control(
                        target, batch_id, run_id, "bronze", table, chunk_no, start_id, end_id, len(chunk), "SUCCESS", started_at, completed_at)

                except Exception as e:
                    # ================================================
                    # LOG TO etl_control | FAILED
                    # ================================================
                    completed_at = datetime.now()

                    save_etl_control(
                        target, batch_id, run_id, "bronze", table, chunk_no, start_id, end_id, len(chunk), "FAILED", started_at, completed_at, str(e))
                    raise

            # =====================================================
            # NO DATA: LOG INTO etl_control and logger
            # =====================================================
            completed_at = datetime.now()
            if not has_data:

                if last_id is None:
                    logger.info(
                        f"Process: Extract | Table: {table} | "
                        f"No records found in source table"
                    )

                    save_etl_control(
                        target, batch_id, run_id, "bronze", table, 0, last_id, last_id, 0, "NO DATA", started_at, completed_at, "No records found in source table")

                else:
                    logger.info(
                        f"Process: Extract | Table: {table} | "
                        f"No new records found | Last ID: {last_id}"
                    )

                    save_etl_control(
                        target, batch_id, run_id, "bronze", table, 0, None, None, 0, "NO DATA", started_at, completed_at, "No new records found in source table")
            else:

                # =====================================================
                # VALIDATE
                # =====================================================
                source_count = get_source_count(
                    table, source, query["column_key"], first_start_id, last_end_id)
                target_count = get_target_count(
                    table, target, query["column_key"], first_start_id, last_end_id)
                if source_count != target_count:

                    for attempt in range(1, max_attempt + 1):

                        try:
                            logger.info(
                                f"WARNING: Initial load | Source table: dbo.{table} | Source total rows: {source_count} | Target total rows: {target_count} | Target table: bronze.{table} | Attempt: {attempt}")

                            # delete incomplete data ===========================================
                            delete_initial_data(
                                table, target, query["column_key"], first_start_id, last_end_id)

                            # load extracted data ===========================================
                            load_initial_data(
                                table, target, source, 'bronze', first_start_id, last_end_id)

                            # Re-check counts after recovery
                            source_count = get_source_count(
                                table, source, query["column_key"], first_start_id, last_end_id)
                            target_count = get_target_count(
                                table, target, query["column_key"], first_start_id, last_end_id)

                            logger.info(
                                f"Validation | Source rows: {source_count} | "
                                f"Target rows: {target_count}")

                            # Stop retry loop if counts match
                            if source_count == target_count:
                                logger.info(
                                    f"Validation successful on attempt {attempt} "
                                    f"for table {table}")
                                break

                        except Exception as e:
                            logger.exception(
                                f"Attempt {attempt} failed")

                            if attempt == max_attempt:
                                raise

                    else:
                        # This executes only if the loop finishes without `break`
                        raise RuntimeError(
                            f"Validation failed after {max_attempt} attempts | "
                            f"Table: {table} | "
                            f"Source rows: {source_count} | "
                            f"Target rows: {target_count}"
                        )

                logger.info(
                    f"LAYER: BRONZE | Table name: {table} | Total Chunk: {chunk_no} | Total rows: {total_rows} | Start ID: {first_start_id} | Last ID: {last_end_id} | STATUS: SUCCESS")

        except Exception as e:

            logger.info(
                f"LAYER: BRONZE | Table name: {table} | Total Chunk: {chunk_no} | Total rows: {total_rows}  | Start ID: {first_start_id} | Last ID: {last_end_id} | STATUS: FAILED")

            raise
