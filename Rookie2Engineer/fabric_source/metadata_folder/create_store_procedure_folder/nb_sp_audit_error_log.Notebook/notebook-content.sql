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

-- Create audit_error_log store procedure
CREATE PROCEDURE audit.sp_insert_error_log
(
    @audit_table_session_id VARCHAR(100),
    @step_name VARCHAR(255),
    @error_code VARCHAR(100),
    @error_name VARCHAR(MAX)
)
AS
BEGIN

    DECLARE @audit_error_id VARCHAR(100);

    SET @audit_error_id = CAST(NEWID() AS VARCHAR(100));

    INSERT INTO audit.audit_error_log
    (
        audit_error_id,
        audit_table_session_id,
        step_name,
        error_code,
        error_name,
        error_time
    )
    VALUES
    (
        @audit_error_id,
        @audit_table_session_id,
        @step_name,
        @error_code,
        @error_name,
        SYSUTCDATETIME()
    );

END;

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }
