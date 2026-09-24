USE DATA_WAREHOUSE;
GO
DROP TABLE etl_control
CREATE TABLE etl_control (
    batch_id VARCHAR(20),
    run_id VARCHAR(36),
    table_schema VARCHAR(20),
    table_name VARCHAR(100),
    chunk_no INT,
    start_id VARCHAR(255),
    end_id VARCHAR(255),
    row_count INT,
    status VARCHAR(20),
    started_at DATETIME2(7),
    completed_at DATETIME2(7),
    error_message VARCHAR(MAX)
)