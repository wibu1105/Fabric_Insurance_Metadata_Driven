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

CREATE PROCEDURE audit.sp_audit_session_log
@action VARCHAR(20),
@audit_session_id VARCHAR(100),
@audit_batch_id VARCHAR(100) = NULL,
@pipeline_name VARCHAR(255) = NULL,
@triggered_by VARCHAR(255) = 'system'

AS
BEGIN

    -- Insert
    IF LOWER(@action) = 'insert'
    BEGIN
        INSERT INTO audit.audit_session_log
        (
            audit_session_id,
            audit_batch_id,
            pipeline_name,
            triggered_by,
            session_status,
            session_start,
            session_end
        )
        VALUES
        (
            @audit_session_id,
            @audit_batch_id,
            @pipeline_name,
            @triggered_by,
            'started',
            CURRENT_TIMESTAMP,
            NULL
        );
    END

    -- Update running
    ELSE IF LOWER(@action) = 'running'
    BEGIN
        UPDATE audit.audit_session_log
        SET session_status = 'running'
        WHERE audit_session_id = @audit_session_id;
    END

    -- Update failed
    ELSE IF LOWER(@action) = 'failed'
    BEGIN
        UPDATE audit.audit_session_log
        SET 
            session_status = 'failed',
            session_end = CURRENT_TIMESTAMP
        WHERE audit_session_id = @audit_session_id;
    END

    -- Update success
    ELSE IF LOWER(@action) = 'success'
    BEGIN
        UPDATE audit.audit_session_log
        SET 
            session_status = 'success',
            session_end = CURRENT_TIMESTAMP
        WHERE audit_session_id = @audit_session_id;
    END
END;


-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }
