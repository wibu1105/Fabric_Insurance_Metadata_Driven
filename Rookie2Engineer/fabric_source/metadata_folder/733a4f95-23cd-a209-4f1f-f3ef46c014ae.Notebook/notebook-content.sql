-- Fabric notebook source

-- METADATA ********************

-- META {
-- META   "kernel_info": {
-- META     "name": "sqldatawarehouse"
-- META   },
-- META   "dependencies": {
-- META     "warehouse": {
-- META       "default_warehouse": "e013e43e-49e8-865d-4824-221f0cbc1668",
-- META       "known_warehouses": [
-- META         {
-- META           "id": "e013e43e-49e8-865d-4824-221f0cbc1668",
-- META           "type": "Datawarehouse"
-- META         }
-- META       ]
-- META     }
-- META   }
-- META }

-- CELL ********************

-- Create schema if not exists
IF NOT EXISTS (
    SELECT 1
    FROM sys.schemas
    WHERE name = 'audit'
)
BEGIN
    EXEC('CREATE SCHEMA audit');
END;
GO

-- 3.1 Batch Log
CREATE TABLE audit.audit_batch_log (
    audit_batch_id      VARCHAR(100),
    batch_name          VARCHAR(255),
    triggered_by        VARCHAR(255),
    batch_status        VARCHAR(50),
    session_start       DATETIME2(0),
    session_end         DATETIME2(0)
);
GO


-- 3.2 Session Log
CREATE TABLE audit.audit_session_log (
    audit_session_id    VARCHAR(100),
    audit_batch_id      VARCHAR(100),
    pipeline_name       VARCHAR(255),
    triggered_by        VARCHAR(255),
    session_status      VARCHAR(50),
    session_start       DATETIME2(0),
    session_end         DATETIME2(0)
);
GO


-- 3.3 Table Session Log
CREATE TABLE audit.audit_table_session_log (
    audit_table_session_id  VARCHAR(100),
    audit_session_id        VARCHAR(100),
    table_id                INT,
    layer_name              VARCHAR(100),
    load_type               VARCHAR(50),
    status                  VARCHAR(50),
    start_time              DATETIME2(0),
    end_time                DATETIME2(0),
    processed_rows          INT,
    created_at              DATETIME2(0),
    updated_at              DATETIME2(0)
);
GO


-- 3.4 Error Log
CREATE TABLE audit.audit_error_log (
    audit_error_id          VARCHAR(100),
    audit_table_session_id  VARCHAR(100),
    step_name               VARCHAR(255),
    error_code              VARCHAR(100),
    error_name              VARCHAR(MAX),
    error_time              DATETIME2(0)
);
GO


-- 3.5 Invalid Record Log
CREATE TABLE audit.audit_invalid_record (
    invalid_record_id       VARCHAR(100),
    audit_table_session_id  VARCHAR(100),
    layer_name              VARCHAR(100),
    table_name              VARCHAR(255),
    invalid_column          VARCHAR(255),
    invalid_reason          VARCHAR(1000),
    invalid_record_count    INT,
    record_payload          VARCHAR(MAX),
    rejected_timestamp      DATETIME2(0)
);
GO

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }
