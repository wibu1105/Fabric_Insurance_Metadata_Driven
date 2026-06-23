# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "1abd17a2-112c-4390-a066-25015003935f",
# META       "default_lakehouse_name": "Rookie2Engineer_Lakehouse",
# META       "default_lakehouse_workspace_id": "5db1b4b5-9a8b-4bf9-808d-ed9af21bd9a8",
# META       "known_lakehouses": [
# META         {
# META           "id": "1abd17a2-112c-4390-a066-25015003935f"
# META         }
# META       ]
# META     }
# META   }
# META }

# CELL ********************

# MAGIC %%sql
# MAGIC 
# MAGIC CREATE TABLE IF NOT EXISTS gold.DimDate(
# MAGIC     date_key BIGINT,
# MAGIC     full_date DATE,
# MAGIC     date_long_description STRING,
# MAGIC     date_short_description STRING,
# MAGIC     day_name STRING,
# MAGIC     day_short_name STRING,
# MAGIC     month_name STRING,
# MAGIC     month_short_name STRING,
# MAGIC     day_of_year INT,
# MAGIC     week_number INT,
# MAGIC     day_of_week INT,
# MAGIC     month_number INT,
# MAGIC     day_of_month INT,
# MAGIC     quarter_number INT,
# MAGIC     day_of_quarter INT,
# MAGIC     year_number INT,
# MAGIC     is_weekend BOOLEAN
# MAGIC )
# MAGIC USING DELTA;
# MAGIC 
# MAGIC CREATE TABLE IF NOT EXISTS gold.DimAgent(
# MAGIC     agent_id STRING,
# MAGIC     agent_key BIGINT,
# MAGIC     agent_name STRING,
# MAGIC     region STRING,
# MAGIC     branch STRING,
# MAGIC     manager_name STRING,
# MAGIC     created_date TIMESTAMP,
# MAGIC     effective_start_date TIMESTAMP,
# MAGIC     effective_end_date TIMESTAMP,
# MAGIC     is_current BOOLEAN
# MAGIC )
# MAGIC USING DELTA;
# MAGIC 
# MAGIC CREATE TABLE IF NOT EXISTS gold.DimPolicyInfo(
# MAGIC     policy_info_key BIGINT,
# MAGIC     policy_id STRING,
# MAGIC     policy_number STRING,
# MAGIC     policy_start_date DATE,
# MAGIC     policy_end_date DATE,
# MAGIC     is_deleted BOOLEAN DEFAULT FALSE
# MAGIC )
# MAGIC USING DELTA
# MAGIC TBLPROPERTIES ('delta.feature.allowColumnDefaults' = 'supported');
# MAGIC 
# MAGIC CREATE TABLE IF NOT EXISTS gold.DimProvider(
# MAGIC     provider_key BIGINT,
# MAGIC     provider_code STRING,
# MAGIC     provider_name STRING,
# MAGIC     provider_group STRING,
# MAGIC     active_flag INT,
# MAGIC     is_deleted BOOLEAN DEFAULT FALSE
# MAGIC )
# MAGIC USING DELTA
# MAGIC TBLPROPERTIES ('delta.feature.allowColumnDefaults' = 'supported');
# MAGIC 
# MAGIC CREATE TABLE IF NOT EXISTS gold.DimVehicle(
# MAGIC     vehicle_key BIGINT,
# MAGIC     customer_key BIGINT,
# MAGIC     vehicle_id STRING,
# MAGIC     plate_number STRING,
# MAGIC     vehicle_brand STRING,
# MAGIC     vehicle_model STRING,
# MAGIC     manufacture_year INT,
# MAGIC     vehicle_value DECIMAL(18,2),
# MAGIC     is_deleted BOOLEAN DEFAULT FALSE
# MAGIC )
# MAGIC USING DELTA
# MAGIC TBLPROPERTIES ('delta.feature.allowColumnDefaults' = 'supported');
# MAGIC 
# MAGIC CREATE TABLE IF NOT EXISTS gold.DimPaymentType(
# MAGIC     payment_type_key BIGINT,
# MAGIC     payment_method STRING,
# MAGIC     payment_description STRING,
# MAGIC     is_deleted BOOLEAN DEFAULT FALSE
# MAGIC )
# MAGIC USING DELTA
# MAGIC TBLPROPERTIES ('delta.feature.allowColumnDefaults' = 'supported');
# MAGIC 
# MAGIC CREATE TABLE IF NOT EXISTS gold.DimCustomer(
# MAGIC     customer_key BIGINT,
# MAGIC     customer_id STRING,
# MAGIC     full_name STRING,
# MAGIC     gender STRING,
# MAGIC     date_of_birth DATE,
# MAGIC     phone_number STRING,
# MAGIC     email STRING,
# MAGIC     city STRING,
# MAGIC     district STRING,
# MAGIC     created_date TIMESTAMP,
# MAGIC     effective_start_date TIMESTAMP,
# MAGIC     effective_end_date TIMESTAMP,
# MAGIC     is_current BOOLEAN
# MAGIC )
# MAGIC USING DELTA;
# MAGIC 
# MAGIC CREATE TABLE IF NOT EXISTS gold.DimQuotationInfo(
# MAGIC     quotation_info_key BIGINT,
# MAGIC     quotation_id STRING,
# MAGIC     package_code STRING,
# MAGIC     is_deleted BOOLEAN DEFAULT FALSE
# MAGIC )
# MAGIC USING DELTA
# MAGIC TBLPROPERTIES ('delta.feature.allowColumnDefaults' = 'supported');
# MAGIC 
# MAGIC CREATE TABLE IF NOT EXISTS gold.FactQuotationItem(
# MAGIC     customer_key BIGINT,
# MAGIC     agent_key BIGINT,
# MAGIC     provider_key BIGINT,
# MAGIC     coverage_type STRING,
# MAGIC     quotation_info_key BIGINT,
# MAGIC     quotation_date_key INT,
# MAGIC     quotation_expiry_date TIMESTAMP,
# MAGIC     quotation_status STRING,
# MAGIC     quotation_premium_amount DECIMAL(18,2),
# MAGIC     quotation_item_id STRING,
# MAGIC     coverage_amount DECIMAL(18,2),
# MAGIC     deductible_amount DECIMAL(18,2)
# MAGIC )
# MAGIC USING DELTA;
# MAGIC 
# MAGIC CREATE TABLE IF NOT EXISTS gold.FactPolicy(
# MAGIC     customer_key BIGINT,
# MAGIC     agent_key BIGINT,
# MAGIC     issue_date_key INT,
# MAGIC     provider_key BIGINT,
# MAGIC     policy_info_key BIGINT,
# MAGIC     quotation_info_key BIGINT,
# MAGIC     policy_status STRING,
# MAGIC     policy_premium_amount DECIMAL(18,2)
# MAGIC )
# MAGIC USING DELTA;
# MAGIC 
# MAGIC CREATE TABLE IF NOT EXISTS gold.FactPayment(
# MAGIC     payment_id STRING,
# MAGIC     customer_key BIGINT,
# MAGIC     agent_key BIGINT,
# MAGIC     provider_key BIGINT,
# MAGIC     policy_info_key BIGINT,
# MAGIC     payment_date_key INT,
# MAGIC     payment_status STRING,
# MAGIC     payment_type_key BIGINT,
# MAGIC     payment_amount DECIMAL(18,2),
# MAGIC     transaction_reference STRING
# MAGIC )
# MAGIC USING DELTA;
# MAGIC 
# MAGIC CREATE TABLE IF NOT EXISTS gold.FactCancellation(
# MAGIC     cancellation_id STRING,
# MAGIC     cancellation_date_key INT,
# MAGIC     customer_key BIGINT,
# MAGIC     agent_key BIGINT,
# MAGIC     provider_key BIGINT,
# MAGIC     policy_info_key BIGINT,
# MAGIC     cancellation_reason STRING,
# MAGIC     refund_amount DECIMAL(18,2)
# MAGIC )
# MAGIC USING DELTA;

# METADATA ********************

# META {
# META   "language": "sparksql",
# META   "language_group": "synapse_pyspark"
# META }
