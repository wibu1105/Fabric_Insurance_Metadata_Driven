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

-- Create audit_invalid_record store procedure
CREATE PROCEDURE audit.sp_insert_invalid_record
(
    @audit_table_session_id VARCHAR(100),
    @layer_name VARCHAR(100),
    @table_name VARCHAR(255),
    @invalid_column VARCHAR(255),
    @invalid_reason VARCHAR(1000),
    @invalid_record_count INT,
    @record_payload VARCHAR(MAX)
)
AS
BEGIN

    DECLARE @invalid_record_id VARCHAR(100);

    SET @invalid_record_id = CAST(NEWID() AS VARCHAR(100));

    INSERT INTO audit.audit_invalid_record
    (
        invalid_record_id,
        audit_table_session_id,
        layer_name,
        table_name,
        invalid_column,
        invalid_reason,
        invalid_record_count,
        record_payload,
        rejected_timestamp
    )
    VALUES
    (
        @invalid_record_id,
        @audit_table_session_id,
        @layer_name,
        @table_name,
        @invalid_column,
        @invalid_reason,
        @invalid_record_count,
        @record_payload,
        CURRENT_TIMESTAMP
    );

END;

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }
