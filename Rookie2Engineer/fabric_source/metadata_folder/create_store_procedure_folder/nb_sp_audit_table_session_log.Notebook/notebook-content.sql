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

CREATE PROCEDURE [audit].[sp_audit_table_session_log]
@action VARCHAR(20),
@audit_table_session_id VARCHAR(100) = NULL,
@audit_session_id VARCHAR(100) = NULL,
@table_id INT = 0,
@layer_name VARCHAR(100) = NULL,
@load_type VARCHAR(50) = NULL,
@processed_rows INT = 0

AS
BEGIN

    -- Insert
    IF LOWER(@action) = 'insert'
    BEGIN
        IF @audit_table_session_id IS NULL
            SET @audit_table_session_id = CAST(NEWID() AS VARCHAR(100));

        INSERT INTO audit.audit_table_session_log
        (
            audit_table_session_id,
            audit_session_id,
            table_id,
            layer_name,
            load_type,
            status,
            start_time,
            end_time,
            processed_rows,
            created_at,
            updated_at
        )
        VALUES
        (
            @audit_table_session_id,
            @audit_session_id,
            @table_id,
            @layer_name,
            @load_type,
            'started',
            CURRENT_TIMESTAMP,
            NULL,
            0,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        );

        -- Trả lại ID vừa insert
        SELECT @audit_table_session_id AS audit_table_session_id;
    END

    -- Update running
    ELSE IF LOWER(@action) = 'running'
    BEGIN
        UPDATE audit.audit_table_session_log
        SET
            status = 'running',
            updated_at = CURRENT_TIMESTAMP
        WHERE audit_table_session_id = @audit_table_session_id;
    END

    -- Update failed
    ELSE IF LOWER(@action) = 'failed'
    BEGIN
        UPDATE audit.audit_table_session_log
        SET
            status = 'failed',
            end_time = CURRENT_TIMESTAMP,
            updated_at = CURRENT_TIMESTAMP
        WHERE audit_table_session_id = @audit_table_session_id;
    END

    -- Update success
    ELSE IF LOWER(@action) = 'success'
    BEGIN
        UPDATE audit.audit_table_session_log
        SET
            status = 'success',
            end_time = CURRENT_TIMESTAMP,
            updated_at = CURRENT_TIMESTAMP,
            processed_rows = @processed_rows
        WHERE audit_table_session_id = @audit_table_session_id;
    END

END;

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }
