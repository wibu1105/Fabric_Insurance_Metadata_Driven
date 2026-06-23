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
# MAGIC CREATE TABLE IF NOT EXISTS bronze.customers(
# MAGIC     customer_id STRING,
# MAGIC     full_name STRING,
# MAGIC     gender STRING,
# MAGIC     dob DATE,
# MAGIC     phone_number STRING,
# MAGIC     email STRING,
# MAGIC     city STRING,
# MAGIC     district STRING,
# MAGIC     created_date TIMESTAMP
# MAGIC )
# MAGIC USING DELTA;
# MAGIC 
# MAGIC CREATE TABLE IF NOT EXISTS bronze.agents(
# MAGIC     agent_id STRING,
# MAGIC     agent_name STRING,
# MAGIC     region STRING,
# MAGIC     branch STRING,
# MAGIC     manager_name STRING,
# MAGIC     created_date TIMESTAMP
# MAGIC )
# MAGIC USING DELTA;
# MAGIC 
# MAGIC CREATE TABLE IF NOT EXISTS bronze.insurance_providers(
# MAGIC     provider_code STRING,
# MAGIC     provider_name STRING,
# MAGIC     provider_group STRING,
# MAGIC     active_flag INT
# MAGIC )
# MAGIC USING DELTA;
# MAGIC 
# MAGIC CREATE TABLE IF NOT EXISTS bronze.vehicle(
# MAGIC     vehicle_id STRING,
# MAGIC     customer_id STRING,
# MAGIC     plate_number STRING,
# MAGIC     vehicle_brand STRING,
# MAGIC     vehicle_model STRING,
# MAGIC     manufacture_year INT,
# MAGIC     vehicle_value DECIMAL(18,2)
# MAGIC )
# MAGIC USING DELTA;
# MAGIC 
# MAGIC CREATE TABLE IF NOT EXISTS bronze.quotation(
# MAGIC     quotation_id STRING,
# MAGIC     customer_id STRING,
# MAGIC     agent_id STRING,
# MAGIC     provider_code STRING,
# MAGIC     quotation_date TIMESTAMP,
# MAGIC     quotation_status STRING,
# MAGIC     package_code STRING,
# MAGIC     premium_amount DECIMAL(18,2),
# MAGIC     quotation_expiry_date TIMESTAMP
# MAGIC )
# MAGIC USING DELTA;
# MAGIC 
# MAGIC CREATE TABLE IF NOT EXISTS bronze.quotation_item(
# MAGIC     quotation_item_id STRING,
# MAGIC     quotation_id STRING,
# MAGIC     coverage_type STRING,
# MAGIC     coverage_amount DECIMAL(18,2),
# MAGIC     deductible_amount DECIMAL(18,2)
# MAGIC )
# MAGIC USING DELTA;
# MAGIC 
# MAGIC CREATE TABLE IF NOT EXISTS bronze.policy(
# MAGIC     policy_id STRING,
# MAGIC     quotation_id STRING,
# MAGIC     customer_id STRING,
# MAGIC     provider_code STRING,
# MAGIC     policy_number STRING,
# MAGIC     policy_start_date DATE,
# MAGIC     policy_end_date DATE,
# MAGIC     policy_status STRING,
# MAGIC     premium_amount DECIMAL(18,2),
# MAGIC     issued_date TIMESTAMP,
# MAGIC     last_updated TIMESTAMP,
# MAGIC     operation_type STRING,
# MAGIC     batch_date DATE,
# MAGIC     source_system STRING
# MAGIC )
# MAGIC USING DELTA;
# MAGIC 
# MAGIC CREATE TABLE IF NOT EXISTS bronze.cancellation(
# MAGIC     cancellation_id STRING,
# MAGIC     policy_id STRING,
# MAGIC     cancellation_date TIMESTAMP,
# MAGIC     cancellation_reason STRING,
# MAGIC     refund_amount DECIMAL(18,2),
# MAGIC     last_updated TIMESTAMP,
# MAGIC     operation_type STRING,
# MAGIC     batch_date DATE,
# MAGIC     source_system STRING
# MAGIC )
# MAGIC USING DELTA;
# MAGIC 
# MAGIC CREATE TABLE IF NOT EXISTS bronze.payment(
# MAGIC     payment_id STRING,
# MAGIC     policy_id STRING,
# MAGIC     payment_date TIMESTAMP,
# MAGIC     payment_method STRING,
# MAGIC     payment_status STRING,
# MAGIC     payment_amount DECIMAL(18,2),
# MAGIC     transaction_reference STRING,
# MAGIC     last_updated TIMESTAMP,
# MAGIC     operation_type STRING,
# MAGIC     batch_date DATE,
# MAGIC     source_system STRING
# MAGIC )
# MAGIC USING DELTA;

# METADATA ********************

# META {
# META   "language": "sparksql",
# META   "language_group": "synapse_pyspark"
# META }
