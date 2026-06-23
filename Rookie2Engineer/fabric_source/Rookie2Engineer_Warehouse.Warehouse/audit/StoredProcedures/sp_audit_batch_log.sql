-- Create audit_bach_log store procedure
CREATE PROCEDURE audit.sp_audit_batch_log
    @action VARCHAR(20),
    @audit_batch_id VARCHAR(100),
    @batch_name VARCHAR(255) = 'Master ETL Pipeline',
    @triggered_by VARCHAR(255) = 'system'
AS
BEGIN

    IF @action = 'insert'
    BEGIN
        INSERT INTO audit.audit_batch_log
        (
            audit_batch_id,
            batch_name,
            triggered_by,
            batch_status,
            session_start,
            session_end
        )
        VALUES
        (
            @audit_batch_id,
            @batch_name,
            @triggered_by,
            'running',
            CURRENT_TIMESTAMP,
            NULL
        );
    END

    ELSE IF @action = 'success'
    BEGIN
        UPDATE audit.audit_batch_log
        SET
            batch_status = 'success',
            session_end = CURRENT_TIMESTAMP
        WHERE audit_batch_id = @audit_batch_id;
    END

    ELSE IF @action = 'failed'
    BEGIN
        UPDATE audit.audit_batch_log
        SET
            batch_status = 'failed',
            session_end = CURRENT_TIMESTAMP
        WHERE audit_batch_id = @audit_batch_id;
    END

END;