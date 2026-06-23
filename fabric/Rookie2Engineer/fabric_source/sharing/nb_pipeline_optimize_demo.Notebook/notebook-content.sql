-- Fabric notebook source

-- METADATA ********************

-- META {
-- META   "kernel_info": {
-- META     "name": "sqldatawarehouse"
-- META   },
-- META   "dependencies": {
-- META     "lakehouse": {
-- META       "default_lakehouse": "1abd17a2-112c-4390-a066-25015003935f",
-- META       "default_lakehouse_name": "Rookie2Engineer_Lakehouse",
-- META       "default_lakehouse_workspace_id": "5db1b4b5-9a8b-4bf9-808d-ed9af21bd9a8",
-- META       "known_lakehouses": [
-- META         {
-- META           "id": "1abd17a2-112c-4390-a066-25015003935f"
-- META         }
-- META       ]
-- META     },
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

select * 
from audit.audit_batch_log
ORDER BY session_start DESC;

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }

-- CELL ********************

SELECT *,
       CONCAT(
           DATEDIFF(SECOND, session_start, session_end) / 60,
           'm ',
           DATEDIFF(SECOND, session_start, session_end) % 60,
           's'
       ) AS batch_time
FROM audit.audit_batch_log
WHERE audit_batch_id = '62f2dcbf-a68b-4eee-8c40-1525de804abe'
ORDER BY session_start DESC;

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }

-- CELL ********************

select *
from audit.audit_session_log
where audit_batch_id = '62f2dcbf-a68b-4eee-8c40-1525de804abe'
order by session_start asc;

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }

-- CELL ********************

select t.* 
from audit.audit_table_session_log t
join audit.audit_session_log s on t.audit_session_id = s.audit_session_id
where s.audit_batch_id = '62f2dcbf-a68b-4eee-8c40-1525de804abe'
order by t.start_time asc;

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }

-- CELL ********************

select *
from cfg.cfg_table_watermark;

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }
