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
target_table = "dimagent"
audit_sink = "warehouse"
audit_warehouse_name = "Rookie2Engineer_Warehouse"
audit_warehouse_workspace_id = ""
audit_warehouse_id = ""
useRootDefaultLakehouse = True

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

import json
import uuid
import builtins
from datetime import datetime

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window
from delta.tables import DeltaTable

spark = SparkSession.builder.getOrCreate()

TARGET_TABLE = f"{target_schema}.{target_table}"

TARGET_COLUMNS = [
    "agent_key",
    "agent_id",
    "agent_name",
    "region",
    "branch",
    "manager_name",
    "created_date",
    "effective_start_date",
    "effective_end_date",
    "is_current",
]

TYPE2_COLUMNS = ["agent_name", "region", "branch", "manager_name"]
TYPE1_COLUMNS = ["created_date"]


# -----------------------------
# Helpers (colleague-style)
# -----------------------------

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

def unknown_member_df():
    return spark.sql("""
        SELECT
            CAST(-1 AS BIGINT) AS agent_key,
            'Unknown' AS agent_id,
            'Unknown Agent' AS agent_name,
            'Unknown' AS region,
            'Unknown' AS branch,
            'Unknown' AS manager_name,
            TO_TIMESTAMP('1900-01-02 00:00:00') AS created_date,
            TO_TIMESTAMP('1900-01-02 00:00:00') AS effective_start_date,
            TO_TIMESTAMP('9999-12-31 23:59:59') AS effective_end_date,
            CAST(TRUE AS BOOLEAN) AS is_current
    """).select(*TARGET_COLUMNS)


def any_column_changed(column_names):
    condition = None
    for c in column_names:
        changed = ~F.col(f"src.{c}").eqNullSafe(F.col(f"tgt.{c}"))
        condition = changed if condition is None else condition | changed
    return condition


def prepare_new_versions(df, effective_start_expression):
    return (
        df.withColumn("effective_start_date", effective_start_expression)
          .withColumn("effective_end_date", F.to_timestamp(F.lit("9999-12-31 23:59:59")))
          .withColumn("is_current", F.lit(True))
    )


def add_surrogate_keys(df, current_max_key):
    start_key = 0 if current_max_key is None else builtins.max(0, int(current_max_key))

    key_window = Window.orderBy("agent_id")

    return (
        df.withColumn(
            "agent_key",
            (F.row_number().over(key_window).cast("bigint") + F.lit(start_key))
        )
        .select(*TARGET_COLUMNS)
    )


def align_to_target_columns(df):
    missing = [c for c in TARGET_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    return df.select([F.col(c) for c in TARGET_COLUMNS])


# -----------------------------
# Core Transform (clean + dedupe)
# -----------------------------

def transform_agents():
    source_df = spark.read.table("silver.agents")
    #source_row_count = source_df.count()    

    clean_df = (
        source_df.select(
            F.trim(F.col("agent_id")).alias("agent_id"),
            F.trim(F.col("agent_name")).alias("agent_name"),
            F.trim(F.col("region")).alias("region"),
            F.trim(F.col("branch")).alias("branch"),
            F.trim(F.col("manager_name")).alias("manager_name"),
            F.to_timestamp(F.col("created_date")).alias("created_date"),
        )
    )

    window_spec = Window.partitionBy("agent_id").orderBy(
        F.col("created_date").desc_nulls_last()
    )

    df = (
        clean_df.withColumn("row_number", F.row_number().over(window_spec))
        .filter(F.col("row_number") == 1)
        .drop("row_number")
    )

    return df


# -----------------------------
# Gold Load (SCD logic)
# -----------------------------

def write_to_gold(source_df, expire_missing_from_source=True):

    if not spark.catalog.tableExists(TARGET_TABLE):
        return initial_load(source_df)

    target_df = spark.read.table(TARGET_TABLE)

    if target_df.count() == 0:
        return initial_load(source_df)

    current_target_df = target_df.filter(F.col("is_current") == True)

    joined_df = source_df.alias("src").join(
        current_target_df.alias("tgt"),
        on="agent_id",
        how="inner"
    )

    changed_type2_df = joined_df.filter(
        any_column_changed(TYPE2_COLUMNS)
    ).select("src.*")

    changed_type2_keys_df = changed_type2_df.select("agent_id").distinct()

    unchanged_df = source_df.alias("src").join(
        changed_type2_keys_df.alias("chg"),
        on="agent_id",
        how="left_anti"
    )

    changed_type1_df = (
        unchanged_df.alias("src")
        .join(current_target_df.alias("tgt"), on="agent_id", how="inner")
        .select("src.*")
    )

    existing_keys_df = target_df.select("agent_id").distinct()

    new_agent_df = source_df.alias("src").join(
        existing_keys_df.alias("tgt"),
        on="agent_id",
        how="left_anti"
    )
    
    delta_table = DeltaTable.forName(spark, TARGET_TABLE)

    processed_rows = 0

    # ---------------- TYPE 1 UPDATE ----------------
    if changed_type1_df.count() > 0:
        delta_table.alias("tgt").merge(
            changed_type1_df.alias("src"),
            "tgt.agent_id = src.agent_id AND tgt.is_current = true"
        ).whenMatchedUpdate(
            set={c: f"src.{c}" for c in TYPE1_COLUMNS}
        ).execute()

        processed_rows += changed_type1_df.count()

    # ---------------- TYPE 2 END-DATE ----------------
    if changed_type2_df.count() > 0:
        delta_table.alias("tgt").merge(
            changed_type2_keys_df.alias("src"),
            "tgt.agent_id = src.agent_id AND tgt.is_current = true"
        ).whenMatchedUpdate(
            set={
                "effective_end_date": "current_timestamp()",
                "is_current": "false"
            }
        ).execute()
    
    # ---------------- INSERT NEW + TYPE2 NEW VERSION ----------------
    append_df = changed_type2_df.unionByName(new_agent_df)

    if append_df.count() > 0:
        max_key = target_df.agg(F.max("agent_key")).first()[0]

        versions = prepare_new_versions(append_df, F.current_timestamp())
        versions = add_surrogate_keys(versions, max_key)

        versions.write.format("delta").mode("append").saveAsTable(TARGET_TABLE)

        processed_rows += append_df.count()
    
    # ---------------- OPTIONAL EXPIRY ----------------
    if expire_missing_from_source:
        source_keys = source_df.select("agent_id").distinct()

        missing_df = (
            current_target_df.alias("tgt")
            .join(source_keys.alias("src"), on="agent_id", how="left_anti")
            .filter(F.col("agent_id") != "Unknown")
        )

        missing_keys = missing_df.select("agent_id").distinct()

        if missing_keys.count() > 0:
            delta_table.alias("tgt").merge(
                missing_keys.alias("src"),
                "tgt.agent_id = src.agent_id AND tgt.is_current = true"
            ).whenMatchedUpdate(
                set={
                    "effective_end_date": "current_timestamp()",
                    "is_current": "false"
                }
            ).execute()

            processed_rows += missing_keys.count()

    return processed_rows


# -----------------------------
# Initial Load
# -----------------------------

def initial_load(source_df):
    versions = prepare_new_versions(source_df, F.current_timestamp())
    versions = add_surrogate_keys(versions, 0)

    final_df = unknown_member_df().unionByName(versions)

    final_df.write.format("delta") \
        .mode("overwrite") \
        .option("overwriteSchema", "true") \
        .saveAsTable(TARGET_TABLE)

    return final_df.count()


# -----------------------------
# Pipeline Execution
# -----------------------------

def run_gold_pipeline():
    start_time = utc_now()

    df = transform_agents()
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
