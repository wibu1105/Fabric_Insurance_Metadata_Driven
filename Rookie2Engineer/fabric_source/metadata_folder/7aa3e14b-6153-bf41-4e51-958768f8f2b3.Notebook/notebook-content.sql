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

INSERT INTO cfg.cfg_silver_gold_table
(
    table_id,
    layer_name,
    target_schema,
    target_table,
    primary_key_column,
    watermark_column,
    notebook_name,
    load_type,
    dependency_level,
    created_date,
    updated_date,
    is_active
)
SELECT *
FROM
(
    VALUES

    -- Silver
    (3001,'silver','silver','customers','customer_id',NULL,'nb_child_customers','full',1,SYSUTCDATETIME(),SYSUTCDATETIME(),1),
    (3002,'silver','silver','agents','agent_id',NULL,'nb_child_agents','full',1,SYSUTCDATETIME(),SYSUTCDATETIME(),1),
    (3003,'silver','silver','insurance_providers','provider_code',NULL,'nb_child_insurance_providers','full',1,SYSUTCDATETIME(),SYSUTCDATETIME(),1),
    (3004,'silver','silver','vehicle','vehicle_id',NULL,'nb_child_vehicle','full',1,SYSUTCDATETIME(),SYSUTCDATETIME(),1),
    (3005,'silver','silver','quotation','quotation_id',NULL,'nb_child_quotation','full',1,SYSUTCDATETIME(),SYSUTCDATETIME(),1),
    (3006,'silver','silver','quotation_item','quotation_item_id',NULL,'nb_child_quotation_item','full',1,SYSUTCDATETIME(),SYSUTCDATETIME(),1),
    (3007,'silver','silver','policy','policy_id','last_updated','nb_child_policy','incremental',1,SYSUTCDATETIME(),SYSUTCDATETIME(),1),
    (3008,'silver','silver','payment','payment_id','last_updated','nb_child_payment','incremental',1,SYSUTCDATETIME(),SYSUTCDATETIME(),1),
    (3009,'silver','silver','cancellation','cancellation_id','last_updated','nb_child_cancellation','incremental',1,SYSUTCDATETIME(),SYSUTCDATETIME(),1),

    -- Gold level 1
    (4001,'gold','gold','DimCustomer','customer_key',NULL,'nb_child_dimcustomer','full',1,SYSUTCDATETIME(),SYSUTCDATETIME(),1),
    (4002,'gold','gold','DimAgent','agent_key',NULL,'nb_child_dimagent','full',1,SYSUTCDATETIME(),SYSUTCDATETIME(),1),
    (4003,'gold','gold','DimProvider','provider_key',NULL,'nb_child_dimprovider','full',1,SYSUTCDATETIME(),SYSUTCDATETIME(),1),
    (4004,'gold','gold','DimPolicyInfo','policy_info_key',NULL,'nb_child_dimpolicyinfo','full',1,SYSUTCDATETIME(),SYSUTCDATETIME(),1),
    (4005,'gold','gold','DimQuotationInfo','quotation_info_key',NULL,'nb_child_dimquotationinfo','full',1,SYSUTCDATETIME(),SYSUTCDATETIME(),1),
    (4006,'gold','gold','DimPaymentType','payment_type_key',NULL,'nb_child_dimpaymenttype','full',1,SYSUTCDATETIME(),SYSUTCDATETIME(),1),

    -- Gold level 2
    (4007,'gold','gold','DimVehicle','vehicle_key',NULL,'nb_child_dimvehicle','full',2,SYSUTCDATETIME(),SYSUTCDATETIME(),1),

    -- Gold level 3
    (4008,'gold','gold','FactQuotationItem','quotation_item_id',NULL,'nb_child_factquotationitem','full',3,SYSUTCDATETIME(),SYSUTCDATETIME(),1),
    (4009,'gold','gold','FactPolicy','policy_info_key',NULL,'nb_child_factpolicy','full',3,SYSUTCDATETIME(),SYSUTCDATETIME(),1),
    (4010,'gold','gold','FactPayment','payment_id',NULL,'nb_child_factpayment','full',3,SYSUTCDATETIME(),SYSUTCDATETIME(),1),
    (4011,'gold','gold','FactCancellation','cancellation_id',NULL,'nb_child_factcancellation','full',3,SYSUTCDATETIME(),SYSUTCDATETIME(),1)

) AS src
(
    table_id,
    layer_name,
    target_schema,
    target_table,
    primary_key_column,
    watermark_column,
    notebook_id,
    load_type,
    dependency_level,
    created_date,
    updated_date,
    is_active
)
WHERE NOT EXISTS
(
    SELECT 1
    FROM cfg.cfg_silver_gold_table t
    WHERE t.table_id = src.table_id
);


-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }
