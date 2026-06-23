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

INSERT INTO cfg.cfg_landing_bronze_table
(
    table_id,
    source_system,
    source_schema,
    source_table,
    source_watermark_column,
    destination_system,
    destination_schema,
    destination_table,
    primary_key_column,
    load_type,
    is_active,
    created_date,
    updated_date
)
VALUES

-- Landing
(1001,'SQLServer_CRM','dbo','agents',NULL,'Lakehouse','landing','agents','agent_id','full',1,SYSUTCDATETIME(),SYSUTCDATETIME()),
(1002,'policy_system',NULL,'cancellation','last_updated','Lakehouse','landing','cancellation','cancellation_id','full',1,SYSUTCDATETIME(),SYSUTCDATETIME()),
(1003,'SQLServer_CRM','dbo','customers',NULL,'Lakehouse','landing','customers','customer_id','full',1,SYSUTCDATETIME(),SYSUTCDATETIME()),
(1004,'SQLServer_CRM','dbo','insurance_providers',NULL,'Lakehouse','landing','insurance_providers','provider_code','full',1,SYSUTCDATETIME(),SYSUTCDATETIME()),
(1005,'payment_system',NULL,'payment','last_updated','Lakehouse','landing','payment','payment_id','full',1,SYSUTCDATETIME(),SYSUTCDATETIME()),
(1006,'policy_system',NULL,'policy','last_updated','Lakehouse','landing','policy','policy_id','full',1,SYSUTCDATETIME(),SYSUTCDATETIME()),
(1007,'SQLServer_CRM','dbo','quotation',NULL,'Lakehouse','landing','quotation','quotation_id','full',1,SYSUTCDATETIME(),SYSUTCDATETIME()),
(1008,'SQLServer_CRM','dbo','quotation_item',NULL,'Lakehouse','landing','quotation_item','quotation_item_id','full',1,SYSUTCDATETIME(),SYSUTCDATETIME()),
(1009,'SQLServer_CRM','dbo','vehicle',NULL,'Lakehouse','landing','vehicle','vehicle_id','full',1,SYSUTCDATETIME(),SYSUTCDATETIME()),

-- Bronze
(2001,'Fabric_Lakehouse','landing','agents',NULL,'Lakehouse','bronze','agents','agent_id','full',1,SYSUTCDATETIME(),SYSUTCDATETIME()),
(2002,'policy_system',NULL,'cancellation','last_updated','Lakehouse','bronze','cancellation','cancellation_id','incremental',1,SYSUTCDATETIME(),SYSUTCDATETIME()),
(2003,'Fabric_Lakehouse','landing','customers',NULL,'Lakehouse','bronze','customers','customer_id','full',1,SYSUTCDATETIME(),SYSUTCDATETIME()),
(2004,'Fabric_Lakehouse','landing','insurance_providers',NULL,'Lakehouse','bronze','insurance_providers','provider_code','full',1,SYSUTCDATETIME(),SYSUTCDATETIME()),
(2005,'payment_system',NULL,'payment','last_updated','Lakehouse','bronze','payment','payment_id','incremental',1,SYSUTCDATETIME(),SYSUTCDATETIME()),
(2006,'policy_system',NULL,'policy','last_updated','Lakehouse','bronze','policy','policy_id','incremental',1,SYSUTCDATETIME(),SYSUTCDATETIME()),
(2007,'Fabric_Lakehouse','landing','quotation',NULL,'Lakehouse','bronze','quotation','quotation_id','full',1,SYSUTCDATETIME(),SYSUTCDATETIME()),
(2008,'Fabric_Lakehouse','landing','quotation_item',NULL,'Lakehouse','bronze','quotation_item','quotation_item_id','full',1,SYSUTCDATETIME(),SYSUTCDATETIME()),
(2009,'Fabric_Lakehouse','landing','vehicle',NULL,'Lakehouse','bronze','vehicle','vehicle_id','full',1,SYSUTCDATETIME(),SYSUTCDATETIME());

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }
