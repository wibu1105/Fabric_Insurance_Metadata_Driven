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

# PARAMETERS CELL ********************

audit_session_id = ""
audit_table_session_id = ""
table_id = ""
load_type = ""
target_schema = "gold"
target_table = "dimprovider"
audit_sink = "warehouse"
audit_warehouse_name = "audit_log"
audit_warehouse_workspace_id = ""
audit_warehouse_id = ""
useRootDefaultLakehouse = True
mark_missing_from_source_as_deleted = False

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from delta.tables import DeltaTable
from pyspark.sql import functions as F
from pyspark.sql import SparkSession
from datetime import datetime
from pyspark.sql.window import Window
import json
import builtins

spark = SparkSession.builder.getOrCreate()

TARGET_TABLE = f"{target_schema}.{target_table}"

TARGET_COLUMNS = ["provider_key", "provider_code", "provider_name", "provider_group", "active_flag", "is_deleted",]

def blank(value):
    return value is None or str(value).strip() == ""


def utc_now():
    return datetime.utcnow()


def iso_utc(value):
    return value.isoformat(timespec="microseconds") + "Z"

def exit_notebook(value):
    out = "" if value is None else str(value)
    try:
        notebookutils.notebook.exit(out)
    except NameError:
        mssparkutils.notebook.exit(out)

def transform():
    source_df = (
        spark.read.table("silver.insurance_providers")
        .select("provider_code", "provider_name", "provider_group", "active_flag")
        .distinct()
    )
    # self.source_row_count = spark.read.table("silver.insurance_providers").count()

    source_df = (
        source_df
        .withColumn("provider_name", F.coalesce(F.col("provider_name"), F.lit("Unknown Provider")))
        .withColumn("provider_code", F.coalesce(F.col("provider_code"), F.lit("Unknown")))
        .withColumn("provider_group", F.coalesce(F.col("provider_name"), F.lit("Unknown Group")))            
        .withColumn("active_flag", F.coalesce(F.col("active_flag"), F.lit(0)))
        .withColumn("is_deleted", F.lit(False))
    )
    return source_df
    
def unknown_member_df():
    unknown_df = spark.sql("""
        SELECT
            CAST(-1 AS BIGINT) AS provider_key,
            'Unknown' AS provider_code,
            'Unknown Provider' AS provider_name,
            'Unknown Group' AS provider_group,
            CAST(0 AS INT) AS active_flag,
            CAST(FALSE AS BOOLEAN) AS is_deleted
    """).select(*TARGET_COLUMNS)

    return unknown_df

def add_surrogate_keys( df, current_max_key):
    start_key = 0 if current_max_key is None else builtins.max(0, int(current_max_key))
    key_window = Window.orderBy("provider_code")

    df = (
        df.withColumn(
            "provider_key",
            F.row_number().over(key_window).cast("bigint") + F.lit(start_key)
        )
        .select(*TARGET_COLUMNS)
    )

    return df

def initial_load( source_df):
    source_df = add_surrogate_keys(source_df, 0)
    df = unknown_member_df().unionByName(source_df)
    processed_rows = df.count()

    (
        df.write.format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(TARGET_TABLE)
    )
    return processed_rows

def write_to_gold( source_df):
    if not spark.catalog.tableExists(TARGET_TABLE):
        return initial_load(source_df)

    target_df = spark.read.table(TARGET_TABLE)
    target_df = target_df.filter(F.col("is_deleted") == False)

    if target_df.count() == 0:
        return initial_load(source_df)

    delta_table = DeltaTable.forName(spark, TARGET_TABLE)
    processed_rows = 0

    existing_provider_df = target_df.select("provider_code").distinct()

    new_provider_df = source_df.alias("src").join(
        existing_provider_df.alias("tgt"),
        on="provider_code",
        how="left_anti"
    )  

    existing_source_df = source_df.alias("src").join(
        existing_provider_df.alias("tgt"),
        on="provider_code",
        how="inner"
    )
        
    existing_source_count = existing_source_df.count()
    if existing_source_count > 0:
        (
            delta_table.alias("tgt")
            .merge(
                existing_source_df.alias("src"),
                "tgt.provider_code = src.provider_code",
            )
            .whenMatchedUpdate(
                condition="tgt.provider_code <> 'Unknown'",
                set={
                    "provider_name":"src.provider_name",
                    "provider_group":"src.provider_group",
                    "active_flag":"src.active_flag",
                    "is_deleted":"src.is_deleted"
                }
            )
            .execute()
        )
        processed_rows += existing_source_count

    new_provider_count = new_provider_df.count()
    if new_provider_count > 0:
        current_max_key = target_df.agg(F.max("provider_key")).first()[0]
        new_provider_df = add_surrogate_keys(new_provider_df, current_max_key)
        (
            new_provider_df.write.format("delta")
            .mode("append")
            .saveAsTable(TARGET_TABLE)
        )
        processed_rows += new_provider_count

    if str(mark_missing_from_source_as_deleted).lower() == "true":
        missing_source_df = target_df.alias("tgt").join(
            source_df.select("provider_code").distinct().alias("src"),
            on="provider_code",
            how="left_anti",
        )
        missing_source_df = missing_source_df.filter(
            F.col("provider_code") != "Unknown"
        ).select("provider_code")

        missing_source_count = missing_source_df.count()
        if missing_source_count > 0:
            (
                delta_table.alias("tgt")
                .merge(
                    missing_source_df.alias("src"),
                    "tgt.provider_code = src.provider_code",
                )
                .whenMatchedUpdate(set={"is_deleted": "true"})
                .execute()
            )
            processed_rows += missing_source_count
    return processed_rows

# -----------------------------
# Pipeline Execution
# -----------------------------

def run_gold_pipeline():
    start_time = utc_now()

    df = transform()
    # output_df = align_to_target_columns(df)
    output_df = df

    processed_rows = write_to_gold(output_df)

    end_time = utc_now()

    return json.dumps({
        "status": "success",
        "target_table": TARGET_TABLE,
        "target_schema": target_schema,
        "audit_table_session_id": audit_table_session_id,
        "processed_rows": processed_rows,
        "start_time": iso_utc(start_time),
        "end_time": iso_utc(end_time),
    }, default=str)


# Execute
result = run_gold_pipeline()
exit_notebook(result)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
