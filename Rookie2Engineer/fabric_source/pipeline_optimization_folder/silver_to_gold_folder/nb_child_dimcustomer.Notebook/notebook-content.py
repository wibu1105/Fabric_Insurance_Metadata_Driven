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
target_table = "dimcustomer"
audit_sink = "warehouse"
audit_warehouse_name = "audit_log"
audit_warehouse_workspace_id = ""
audit_warehouse_id = ""
useRootDefaultLakehouse = True
expire_missing_from_source = False

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

TARGET_COLUMNS = [
        "customer_key",
        "customer_id",
        "full_name",
        "gender",
        "date_of_birth",
        "phone_number",
        "email",
        "city",
        "district",
        "created_date",
        "effective_start_date",
        "effective_end_date",
        "is_current",
    ]

TYPE2_COLUMNS = ["full_name", "city", "district", "phone_number", "email"]
TYPE1_COLUMNS = ["gender", "date_of_birth",  "created_date"]

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
    source_df = spark.read.table('silver.customers')
    # self.source_row_count = source_df.count()

    clean_df = (
        source_df.select(
            F.trim(F.col("customer_id")).alias("customer_id"),
            F.trim(F.col("full_name")).alias("full_name"),
            F.trim(F.col("gender")).alias("gender"),
            F.to_date(F.col("dob")).alias("date_of_birth"),
            F.trim(F.col("phone_number")).alias("phone_number"),
            F.lower(F.trim(F.col("email"))).alias("email"),
            F.trim(F.col("city")).alias("city"),
            F.trim(F.col("district")).alias("district"),
            F.to_timestamp(F.col("created_date")).alias("created_date"),
        )
    )

    window_spec = Window.partitionBy("customer_id").orderBy(
        F.col("created_date").desc_nulls_last()
    )

    df = (
        clean_df.withColumn("row_number", F.row_number().over(window_spec))
        .filter(F.col("row_number") == 1)
        .drop("row_number")
    )

    return df

def unknown_member_df():
    return spark.sql(
        """
        SELECT
            CAST(-1 AS BIGINT) AS customer_key,
            'Unknown' AS customer_id,
            'Unknown Customer' AS full_name,
            'U' AS gender,
            TO_DATE('1900-01-02') AS date_of_birth,
            'N/A' AS phone_number,
            'N/A' AS email,
            'Unknown' AS city,
            'Unknown' AS district,
            TO_TIMESTAMP('1900-01-02 00:00:00') AS created_date,
            TO_TIMESTAMP('1900-01-02 00:00:00') AS effective_start_date,
            TO_TIMESTAMP('9999-12-31 23:59:59') AS effective_end_date,
            CAST(TRUE AS BOOLEAN) AS is_current
        """
    ).select(*TARGET_COLUMNS)

def any_column_changed( column_names):
    condition = None
    for column_name in column_names:
        column_changed = ~F.col(f"src.{column_name}").eqNullSafe(
            F.col(f"tgt.{column_name}")
        )
        condition = column_changed if condition is None else condition | column_changed
    return condition

def add_surrogate_keys( df, current_max_key):
    start_key = 0 if current_max_key is None else builtins.max(0, int(current_max_key))
    key_window = Window.orderBy("customer_id")
    return (
        df.withColumn(
            "customer_key",
            F.row_number().over(key_window).cast("bigint") + F.lit(start_key),
        )
        .select(*TARGET_COLUMNS)
    )

def prepare_new_versions( df, effective_start_expression):
    return (
        df.withColumn("effective_start_date", effective_start_expression)
        .withColumn(
            "effective_end_date",
            F.to_timestamp(F.lit("9999-12-31 23:59:59")),
        )
        .withColumn("is_current", F.lit(True))
    )

def initial_load( source_df):
    source_versions = prepare_new_versions(
        source_df,
        F.current_timestamp(),
    )
    source_versions = add_surrogate_keys(source_versions, 0)
    output_df = unknown_member_df().unionByName(source_versions)

    processed_rows = output_df.count()
    (
        output_df.write.format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(TARGET_TABLE)
    )
    return processed_rows

def write_to_gold( source_df):
    if not spark.catalog.tableExists(TARGET_TABLE):
        return initial_load(source_df)

    target_df = spark.read.table(TARGET_TABLE)

    if target_df.count() == 0:
        return initial_load(source_df)

    current_target_df = target_df.filter(F.col("is_current") == True)

    joined_df = source_df.alias("src").join(
        current_target_df.alias("tgt"),
        on="customer_id",
        how="inner",
    )

    changed_type2_df = joined_df.filter(
        any_column_changed(TYPE2_COLUMNS)
    ).select("src.*")
    changed_type2_keys_df = changed_type2_df.select("customer_id").distinct()

    unchanged_type2_source_df = source_df.alias("src").join(
        changed_type2_keys_df.alias("chg"),
        on="customer_id",
        how="left_anti",
    )

    changed_type1_df = (
        unchanged_type2_source_df.alias("src")
        .join(current_target_df.alias("tgt"), on="customer_id", how="inner")
        .filter(any_column_changed(TYPE1_COLUMNS))
        .select("src.*")
    )

    existing_customer_keys_df = target_df.select("customer_id").distinct()
    new_customer_df = source_df.alias("src").join(
        existing_customer_keys_df.alias("tgt"),
        on="customer_id",
        how="left_anti",
    )

    delta_table = DeltaTable.forName(spark, TARGET_TABLE)
    processed_rows = 0

    changed_type1_count = changed_type1_df.count()
    if changed_type1_count > 0:
        type1_update_set = {
            column_name: f"src.{column_name}" for column_name in TYPE1_COLUMNS
        }
        (
            delta_table.alias("tgt")
            .merge(
                changed_type1_df.alias("src"),
                "tgt.customer_id = src.customer_id AND tgt.is_current = true",
            )
            .whenMatchedUpdate(set=type1_update_set)
            .execute()
        )
        processed_rows += changed_type1_count

    changed_type2_count = changed_type2_df.count()
    if changed_type2_count > 0:
        (
            delta_table.alias("tgt")
            .merge(
                changed_type2_keys_df.alias("src"),
                "tgt.customer_id = src.customer_id AND tgt.is_current = true",
            )
            .whenMatchedUpdate(
                set={
                    "effective_end_date": "current_timestamp()",
                    "is_current": "false",
                }
            )
            .execute()
        )

    append_source_df = changed_type2_df.unionByName(new_customer_df)
    append_source_count = append_source_df.count()
    if append_source_count > 0:
        current_max_key = target_df.agg(F.max("customer_key")).first()[0]
        append_versions_df = prepare_new_versions(
            append_source_df,
            F.current_timestamp(),
        )
        append_versions_df = add_surrogate_keys(
            append_versions_df,
            current_max_key,
        )
        (
            append_versions_df.write.format("delta")
            .mode("append")
            .saveAsTable(TARGET_TABLE)
        )
        processed_rows += append_source_count

    if str(expire_missing_from_source).lower() == "true":
        source_keys_df = source_df.select("customer_id").distinct()

        missing_from_source_df = (
            current_target_df.alias("tgt")
            .join(
                source_keys_df.alias("src"),
                on="customer_id",
                how="left_anti",
            )
            .filter(F.col("customer_id") != "Unknown")
        )

        missing_from_source_df.select(
            "customer_id",
            "full_name",
            "phone_number",
            "email",
            "city",
            "district",
            "effective_start_date",
            "effective_end_date",
            "is_current",
        ).show(truncate=False)

        missing_source_keys_df = missing_from_source_df.select("customer_id").distinct()

        missing_source_count = missing_source_keys_df.count()
        if missing_source_count > 0:
            (
                delta_table.alias("tgt")
                .merge(
                    missing_source_keys_df.alias("src"),
                    "tgt.customer_id = src.customer_id AND tgt.is_current = true",
                )
                .whenMatchedUpdate(
                    set={
                        "effective_end_date": "current_timestamp()",
                        "is_current": "false",
                    }
                )
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
