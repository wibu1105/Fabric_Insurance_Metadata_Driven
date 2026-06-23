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
    WHERE name = 'cfg'
)
BEGIN
    EXEC('CREATE SCHEMA cfg');
END;
GO


-- 2.1 Landing & Bronze Configuration
CREATE TABLE cfg.cfg_landing_bronze_table (
    table_id                    INT,
    source_system               VARCHAR(100),
    source_schema               VARCHAR(100),
    source_table                VARCHAR(255),
    source_watermark_column     VARCHAR(255),
    destination_system          VARCHAR(100),
    destination_schema          VARCHAR(100),
    destination_table           VARCHAR(255),
    primary_key_column          VARCHAR(500),
    load_type                   VARCHAR(50),
    is_active                   BIT,
    created_date                DATETIME2(0),
    updated_date                DATETIME2(0)
);
GO


-- 2.2 Silver & Gold Configuration
CREATE TABLE cfg.cfg_silver_gold_table (
    table_id                INT,
    layer_name              VARCHAR(50),
    target_schema           VARCHAR(100),
    target_table            VARCHAR(255),
    primary_key_column      VARCHAR(500),
    watermark_column        VARCHAR(255),
    notebook_name           VARCHAR(100),
    load_type               VARCHAR(50),
    dependency_level        INT,
    is_active               BIT,
    created_date            DATETIME2(0),
    updated_date            DATETIME2(0)
);
GO


-- 2.3 Watermark Configuration
CREATE TABLE cfg.cfg_table_watermark (
    table_id                INT,
    last_watermark_value    DATETIME2(0),
    last_audit_session      VARCHAR(100),
    last_load_time          DATETIME2(0),
    created_date            DATETIME2(0),
    updated_date            DATETIME2(0)
);
GO

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }
