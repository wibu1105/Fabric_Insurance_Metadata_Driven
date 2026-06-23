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

-- MARKDOWN ********************

-- ## Data Recovery Test Case

-- MARKDOWN ********************

-- ### Test Case of Landing Layer

-- CELL ********************

-- Dữ liệu test recovery tầng landing
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
    'test_landing_recovery_batch_id',
    'Master ETL Pipeline',
    'system',
    'failed',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

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
('test_landing_recovery_session_id','test_landing_recovery_batch_id','pl_source_to_landing_optimize','system','failed',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);

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
('test_landing_recovery_table_01','test_landing_recovery_session_id',1001,'landing','full','failed',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,0,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_landing_recovery_table_02','test_landing_recovery_session_id',1002,'landing','full','success',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,1000,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_landing_recovery_table_03','test_landing_recovery_session_id',1003,'landing','full','success',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,1000,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_landing_recovery_table_04','test_landing_recovery_session_id',1004,'landing','full','success',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,1000,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_landing_recovery_table_05','test_landing_recovery_session_id',1005,'landing','full','failed',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,0,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_landing_recovery_table_06','test_landing_recovery_session_id',1006,'landing','full','failed',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,0,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_landing_recovery_table_07','test_landing_recovery_session_id',1007,'landing','full','success',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,1000,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_landing_recovery_table_08','test_landing_recovery_session_id',1008,'landing','full','success',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,1000,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_landing_recovery_table_09','test_landing_recovery_session_id',1009,'landing','full','failed',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,0,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }

-- CELL ********************

select * from audit.audit_batch_log
where audit_batch_id = 'test_landing_recovery_batch_id'

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }

-- CELL ********************

select * from audit.audit_session_log
where audit_batch_id = 'test_landing_recovery_batch_id'

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }

-- CELL ********************

select t.* from audit.audit_table_session_log t
join audit.audit_session_log s on t.audit_session_id = s.audit_session_id
where s.audit_batch_id = 'test_landing_recovery_batch_id'
order by t.start_time asc;

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }

-- MARKDOWN ********************

-- ### Test Case of Bronze Layer

-- CELL ********************

-- Dữ liệu test recovery tầng bronze
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
    'test_bronze_recovery_batch_id',
    'Master ETL Pipeline',
    'system',
    'failed',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

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
('test_bronze_recovery_session_id_01','test_bronze_recovery_batch_id','pl_source_to_landing_optimize','system','success',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_bronze_recovery_session_id_02','test_bronze_recovery_batch_id','pl_landing_to_bronze_optimize','system','failed',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP)
;

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
('test_bronze_recovery_table_01','test_bronze_recovery_session_id_02',2001,'bronze','full','success',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,4,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_bronze_recovery_table_02','test_bronze_recovery_session_id_02',2002,'bronze','incremental','success',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,60,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_bronze_recovery_table_03','test_bronze_recovery_session_id_02',2003,'bronze','full','failed',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,0,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_bronze_recovery_table_04','test_bronze_recovery_session_id_02',2004,'bronze','full','failed',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,0,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_bronze_recovery_table_05','test_bronze_recovery_session_id_02',2005,'bronze','incremental','failed',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,0,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_bronze_recovery_table_06','test_bronze_recovery_session_id_02',2006,'bronze','incremental','failed',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,0,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_bronze_recovery_table_07','test_bronze_recovery_session_id_02',2007,'bronze','full','success',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,1000,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_bronze_recovery_table_08','test_bronze_recovery_session_id_02',2008,'bronze','full','success',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,1000,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_bronze_recovery_table_09','test_bronze_recovery_session_id_02',2009,'bronze','full','success',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,100,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }

-- CELL ********************

select * from audit.audit_batch_log
where audit_batch_id = 'test_bronze_recovery_batch_id'

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }

-- CELL ********************

select * from audit.audit_session_log
where audit_batch_id = 'test_bronze_recovery_batch_id'

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }

-- CELL ********************

select t.* from audit.audit_table_session_log t
join audit.audit_session_log s on t.audit_session_id = s.audit_session_id
where s.audit_batch_id = 'test_bronze_recovery_batch_id'
order by t.start_time asc;

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }

-- MARKDOWN ********************

-- ### Test Case of Silver Layer

-- CELL ********************

-- Dữ liệu test recovery tầng silver
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
    'test_silver_recovery_batch_id',
    'Master ETL Pipeline',
    'system',
    'failed',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

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
('test_silver_recovery_session_id_01','test_silver_recovery_batch_id','pl_source_to_landing_optimize','system','success',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_silver_recovery_session_id_02','test_silver_recovery_batch_id','pl_landing_to_bronze_optimize','system','success',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_silver_recovery_session_id_03','test_silver_recovery_batch_id','pl_bronze_to_silver_optimize','system','failed',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP)
;

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
('test_silver_recovery_table_01','test_silver_recovery_session_id_03',3001,'silver','full','success',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,1000,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_silver_recovery_table_02','test_silver_recovery_session_id_03',3002,'silver','full','failed',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,0,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_silver_recovery_table_03','test_silver_recovery_session_id_03',3003,'silver','full','failed',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,0,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_silver_recovery_table_04','test_silver_recovery_session_id_03',3004,'silver','full','success',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,1000,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_silver_recovery_table_05','test_silver_recovery_session_id_03',3005,'silver','full','success',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,1000,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_silver_recovery_table_06','test_silver_recovery_session_id_03',3006,'silver','full','success',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,1000,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_silver_recovery_table_07','test_silver_recovery_session_id_03',3007,'silver','incremental','success',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,600,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_silver_recovery_table_08','test_silver_recovery_session_id_03',3008,'silver','incremental','failed',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,0,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_silver_recovery_table_09','test_silver_recovery_session_id_03',3009,'silver','incremental','failed',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,0,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }

-- CELL ********************

select * from audit.audit_batch_log
where audit_batch_id = 'test_silver_recovery_batch_id'

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }

-- CELL ********************

select * from audit.audit_session_log
where audit_batch_id = 'test_silver_recovery_batch_id'

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }

-- CELL ********************

select t.* from audit.audit_table_session_log t
join audit.audit_session_log s on t.audit_session_id = s.audit_session_id
where s.audit_batch_id = 'test_silver_recovery_batch_id'
order by t.start_time asc;

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }

-- MARKDOWN ********************

-- ### Test Case of Gold Layer (Failed in Dependency Level = 1)

-- CELL ********************

-- Dữ liệu test luồng recovery tầng gold (dependency level = 01)

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
    'test_gold_recovery_batch_id_01',
    'Master ETL Pipeline',
    'system',
    'failed',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

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
('test_gold_recovery_session_id_01_01','test_gold_recovery_batch_id_01','pl_source_to_landing_optimize','system','success',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_gold_recovery_session_id_01_02','test_gold_recovery_batch_id_01','pl_landing_to_bronze_optimize','system','success',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_gold_recovery_session_id_01_03','test_gold_recovery_batch_id_01','pl_bronze_to_silver_optimize','system','success',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_gold_recovery_session_id_01_04','test_gold_recovery_batch_id_01','pl_silver_to_gold_optimize','system','failed',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);

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
('test_gold_recovery_table_01_01','test_gold_recovery_session_id_01_04',4005,'gold','full','failed',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,0,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_gold_recovery_table_01_02','test_gold_recovery_session_id_01_04',4003,'gold','full','success',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,7,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_gold_recovery_table_01_03','test_gold_recovery_session_id_01_04',4006,'gold','full','success',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,4,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_gold_recovery_table_01_04','test_gold_recovery_session_id_01_04',4002,'gold','full','success',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,5,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_gold_recovery_table_01_05','test_gold_recovery_session_id_01_04',4004,'gold','full','failed',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,0,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_gold_recovery_table_01_06','test_gold_recovery_session_id_01_04',4001,'gold','full','failed',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,0,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }

-- CELL ********************

select * from audit.audit_batch_log
where audit_batch_id = 'test_gold_recovery_batch_id_01'

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }

-- CELL ********************

select * from audit.audit_session_log
where audit_batch_id = 'test_gold_recovery_batch_id_01'

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }

-- CELL ********************

select t.* from audit.audit_table_session_log t
inner join audit.audit_session_log s on t.audit_session_id = s.audit_session_id
where s.audit_batch_id = 'test_gold_recovery_batch_id_01'
order by t.start_time asc;

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }

-- MARKDOWN ********************

-- ### Test Case of Gold Layer (Failed in Dependency Level = 2)

-- CELL ********************

-- Dữ liệu test luồng recovery tầng gold (dependency level = 02)

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
    'test_gold_recovery_batch_id_02',
    'Master ETL Pipeline',
    'system',
    'failed',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

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
('test_gold_recovery_session_id_02_01','test_gold_recovery_batch_id_02','pl_source_to_landing_optimize','system','success',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_gold_recovery_session_id_02_02','test_gold_recovery_batch_id_02','pl_landing_to_bronze_optimize','system','success',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_gold_recovery_session_id_02_03','test_gold_recovery_batch_id_02','pl_bronze_to_silver_optimize','system','success',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_gold_recovery_session_id_02_04','test_gold_recovery_batch_id_02','pl_silver_to_gold_optimize','system','failed',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);

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
('test_gold_recovery_table_02_01','test_gold_recovery_session_id_02_04',4005,'gold','full','success',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,1001,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_gold_recovery_table_02_02','test_gold_recovery_session_id_02_04',4003,'gold','full','success',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,7,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_gold_recovery_table_02_03','test_gold_recovery_session_id_02_04',4006,'gold','full','success',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,4,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_gold_recovery_table_02_04','test_gold_recovery_session_id_02_04',4002,'gold','full','success',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,5,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_gold_recovery_table_02_05','test_gold_recovery_session_id_02_04',4004,'gold','full','success',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,601,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_gold_recovery_table_02_06','test_gold_recovery_session_id_02_04',4001,'gold','full','success',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,1001,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_gold_recovery_table_02_07','test_gold_recovery_session_id_02_04',4007,'gold','full','failed',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,0,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }

-- CELL ********************

select * from audit.audit_batch_log
where audit_batch_id = 'test_gold_recovery_batch_id_02'

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }

-- CELL ********************

select * from audit.audit_session_log
where audit_batch_id = 'test_gold_recovery_batch_id_02'

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }

-- CELL ********************

select t.* from audit.audit_table_session_log t
inner join audit.audit_session_log s on t.audit_session_id = s.audit_session_id
where s.audit_batch_id = 'test_gold_recovery_batch_id_02'
order by t.start_time asc;

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }

-- MARKDOWN ********************

-- ### Test Case of Gold Layer (Failed in Dependency Level = 3)

-- CELL ********************

-- Dữ liệu test luồng recovery tầng gold (dependency level = 03)

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
    'test_gold_recovery_batch_id_03',
    'Master ETL Pipeline',
    'system',
    'failed',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

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
('test_gold_recovery_session_id_03_01','test_gold_recovery_batch_id_03','pl_source_to_landing_optimize','system','success',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_gold_recovery_session_id_03_02','test_gold_recovery_batch_id_03','pl_landing_to_bronze_optimize','system','success',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_gold_recovery_session_id_03_03','test_gold_recovery_batch_id_03','pl_bronze_to_silver_optimize','system','success',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_gold_recovery_session_id_03_04','test_gold_recovery_batch_id_03','pl_silver_to_gold_optimize','system','failed',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);

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
('test_gold_recovery_table_03_01','test_gold_recovery_session_id_03_04',4005,'gold','full','success',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,1001,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_gold_recovery_table_03_02','test_gold_recovery_session_id_03_04',4003,'gold','full','success',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,7,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_gold_recovery_table_03_03','test_gold_recovery_session_id_03_04',4006,'gold','full','success',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,4,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_gold_recovery_table_03_04','test_gold_recovery_session_id_03_04',4002,'gold','full','success',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,5,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_gold_recovery_table_03_05','test_gold_recovery_session_id_03_04',4004,'gold','full','success',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,601,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_gold_recovery_table_03_06','test_gold_recovery_session_id_03_04',4001,'gold','full','success',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,1001,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_gold_recovery_table_03_07','test_gold_recovery_session_id_03_04',4007,'gold','full','success',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,1001,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_gold_recovery_table_03_08','test_gold_recovery_session_id_03_04',4008,'gold','full','success',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,1000,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_gold_recovery_table_03_09','test_gold_recovery_session_id_03_04',4009,'gold','full','success',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,600,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_gold_recovery_table_03_10','test_gold_recovery_session_id_03_04',4010,'gold','full','failed',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,0,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),
('test_gold_recovery_table_03_11','test_gold_recovery_session_id_03_04',4011,'gold','full','failed',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,0,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }

-- CELL ********************

select * from audit.audit_batch_log
where audit_batch_id = 'test_gold_recovery_batch_id_03'

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }

-- CELL ********************

select * from audit.audit_session_log
where audit_batch_id = 'test_gold_recovery_batch_id_03'

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }

-- CELL ********************

select t.* from audit.audit_table_session_log t
inner join audit.audit_session_log s on t.audit_session_id = s.audit_session_id
where s.audit_batch_id = 'test_gold_recovery_batch_id_03'
order by t.start_time asc;

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }
