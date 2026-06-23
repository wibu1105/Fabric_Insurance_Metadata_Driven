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
# MAGIC -- Drop all tables
# MAGIC DROP SCHEMA IF EXISTS landing;
# MAGIC DROP SCHEMA IF EXISTS bronze;
# MAGIC DROP SCHEMA IF EXISTS silver;
# MAGIC DROP SCHEMA IF EXISTS gold;
# MAGIC DROP SCHEMA IF EXISTS etl;
# MAGIC 
# MAGIC -- Landing: raw data
# MAGIC CREATE SCHEMA landing;
# MAGIC 
# MAGIC -- Bronze: Loadwith metadata
# MAGIC CREATE SCHEMA bronze;
# MAGIC 
# MAGIC -- Silver: cleaned, standardized, deduplicated data
# MAGIC CREATE SCHEMA silver;
# MAGIC 
# MAGIC -- Gold: dimensional/reporting layer
# MAGIC CREATE SCHEMA gold;
# MAGIC 
# MAGIC -- Etl: configuration, control, audit, and error logging
# MAGIC CREATE SCHEMA etl;
# MAGIC 
# MAGIC SHOW SCHEMAS;

# METADATA ********************

# META {
# META   "language": "sparksql",
# META   "language_group": "synapse_pyspark"
# META }
