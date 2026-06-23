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
# META     },
# META     "warehouse": {
# META       "default_warehouse": "e013e43e-49e8-865d-4824-221f0cbc1668",
# META       "known_warehouses": [
# META         {
# META           "id": "e013e43e-49e8-865d-4824-221f0cbc1668",
# META           "type": "Datawarehouse"
# META         }
# META       ]
# META     }
# META   }
# META }

# CELL ********************

# Read the two config tables
df_landing_bronze = spark.read.table("cfg.cfg_landing_bronze_table")
df_silver_gold = spark.read.table("cfg.cfg_silver_gold_table")

# Select and rename columns so they match
df1 = df_landing_bronze.selectExpr("table_id", "destination_table as table_name", "'Landing/Bronze' as cfg_source")
df2 = df_silver_gold.selectExpr("table_id", "target_table as table_name", "'Silver/Gold' as cfg_source")

# Union them together
df_union = df1.union(df2)

# Write to a new physical Delta table
df_union.write.format("delta").mode("overwrite").saveAsTable("bi.dim_table_list")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# MAGIC %%sql
# MAGIC -- Add a column that automatically extracts the Date from the Timestamp
# MAGIC ALTER TABLE audit.audit_batch_log 
# MAGIC ADD COLUMN session_date DATE GENERATED ALWAYS AS (CAST(session_start AS DATE));

# METADATA ********************

# META {
# META   "language": "sparksql",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# MAGIC %%sql
# MAGIC update cfg.cfg_silver_gold_table set notebook_id = '15826c66-126e-409b-9e8c-7f1ddb1ccb98'
# MAGIC where table_id = 4014

# METADATA ********************

# META {
# META   "language": "sparksql",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

df = spark.sql("SELECT * FROM Rookie2Engineer_Lakehouse.cfg.cfg_silver_gold_table LIMIT 1000")
display(df)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# MAGIC %%sql
# MAGIC update audit.audit_table_session_log
# MAGIC set status = 'success' where status = 'Succeeded'

# METADATA ********************

# META {
# META   "language": "sql",
# META   "language_group": "sqldatawarehouse"
# META }

# CELL ********************

# Make sure your cell is set to PySpark (Python)
table = [
    "landing.agents",
    "landing.customers",
    "landing.insurance_providers",
    "landing.quotation",
    "landing.quotation_item",
    "landing.vehicle",
    "bronze.agents",
    "bronze.cancellation",
    "bronze.customers",
    "bronze.insurance_providers",
    "bronze.payment",
    "bronze.policy",
    "bronze.quotation",
    "bronze.quotation_item",
    "bronze.vehicle",
    "silver.agents",
    "silver.cancellation",
    "silver.customers",
    "silver.insurance_providers",
    "silver.payment",
    "silver.policy",
    "silver.quotation",
    "silver.quotation_item",
    "silver.vehicle",
    "gold.dimagent",
    "gold.dimcustomer",
    "gold.dimpaymenttype",
    "gold.dimpolicyinfo",
    "gold.dimprovider",
    "gold.dimquotationinfo",
    "gold.dimvehicle",
    "gold.factcancellation",
    "gold.factpayment",
    "gold.factpolicy",
    "gold.factquotationitem"
]

for table_item in table:
    try:
        # Split the string "schema.tablename" into two separate variables
        schema, table_name = table_item.split('.')
        
        # Wrap the schema and the table individually in backticks
        spark.sql(f"""
            TRUNCATE TABLE `{schema}`.`{table_name}`
        """)    
        print(f"Truncated {table_item} successfully")
        
    except Exception as e:
        print(f"Error at {table_item} | {e}")

# 1. Delete the 'landing' directory and everything inside it (recurse=True)
mssparkutils.fs.rm("Files/landing", True)

# 2. Recreate the empty 'landing' directory
mssparkutils.fs.mkdirs("Files/landing")

print("The landing folder has been emptied successfully.")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
