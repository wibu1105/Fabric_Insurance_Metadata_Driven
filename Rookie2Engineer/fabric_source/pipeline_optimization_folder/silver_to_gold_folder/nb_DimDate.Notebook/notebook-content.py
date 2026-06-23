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
# MAGIC -- 1. Create the Delta Table 
# MAGIC CREATE OR REPLACE TABLE gold.dimdate (
# MAGIC     date_key INT,
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
# MAGIC     is_weekend INT,
# MAGIC     month_year STRING,
# MAGIC     month_year_sort INT
# MAGIC ) USING DELTA;
# MAGIC -- 2. Generate and Insert the Date Sequence
# MAGIC WITH dates AS (
# MAGIC     SELECT explode(sequence(to_date('2000-01-01'), to_date('2099-12-31'), interval 1 day)) AS full_date
# MAGIC )
# MAGIC INSERT OVERWRITE TABLE gold.dimdate
# MAGIC SELECT
# MAGIC     cast(date_format(full_date, 'yyyyMMdd') as int) AS date_key,
# MAGIC     full_date,
# MAGIC     concat(date_format(full_date, 'EEEE'), ', ', date_format(full_date, 'MMMM'), ' ', cast(day(full_date) as string), ', ', cast(year(full_date) as string)) AS date_long_description,
# MAGIC     concat(date_format(full_date, 'MMM'), ' ', cast(day(full_date) as string), ', ', cast(year(full_date) as string)) AS date_short_description,
# MAGIC     date_format(full_date, 'EEEE') AS day_name,
# MAGIC     date_format(full_date, 'EEE') AS day_short_name,
# MAGIC     date_format(full_date, 'MMMM') AS month_name,
# MAGIC     date_format(full_date, 'MMM') AS month_short_name,
# MAGIC     dayofyear(full_date) AS day_of_year,
# MAGIC     weekofyear(full_date) AS week_number,
# MAGIC     dayofweek(full_date) AS day_of_week, 
# MAGIC     month(full_date) AS month_number,
# MAGIC     day(full_date) AS day_of_month,
# MAGIC     quarter(full_date) AS quarter_number,
# MAGIC     datediff(full_date, trunc(full_date, 'QUARTER')) + 1 AS day_of_quarter,
# MAGIC     year(full_date) AS year_number,
# MAGIC     CASE 
# MAGIC         -- In Spark, dayofweek evaluates Sunday as 1 and Saturday as 7
# MAGIC         WHEN dayofweek(full_date) IN (1, 7) THEN 1 
# MAGIC         ELSE 0 
# MAGIC     END AS is_weekend,
# MAGIC     
# MAGIC     -- New Columns for the Power BI Slicer
# MAGIC     date_format(full_date, 'MM-yyyy') AS month_year,
# MAGIC     cast(date_format(full_date, 'yyyyMM') as int) AS month_year_sort
# MAGIC     
# MAGIC FROM dates;
# MAGIC -- 3. Verify execution
# MAGIC SELECT count(*) as insert_count FROM gold.dimdate;

# METADATA ********************

# META {
# META   "language": "sparksql",
# META   "language_group": "synapse_pyspark"
# META }
