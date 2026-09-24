import logging
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# ETL CONTROL =================================================================
def save_etl_control(target_engine, batch_id, run_id, schema, table_name, chunk_no, start_id, end_id, row_count, status, started_at, completed_at, error_message=None):

    data = pd.DataFrame([{
        "batch_id": batch_id,
        "run_id": run_id,
        "table_schema": schema,
        "table_name": table_name,
        "chunk_no": chunk_no,
        "start_id": str(start_id),
        "end_id": str(end_id),
        "row_count": row_count,
        "status": status,
        "started_at": started_at,
        "completed_at": completed_at,
        "error_message": error_message
    }])

    data.to_sql(
        "etl_control",
        con=target_engine,
        if_exists="append",
        index=False
    )
