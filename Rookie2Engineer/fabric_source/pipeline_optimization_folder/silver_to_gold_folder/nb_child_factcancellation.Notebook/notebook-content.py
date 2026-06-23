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

target_schema = "gold"
target_table = "factcancellation"
table_id = 4017

source_cancellation_table = "silver.cancellation"
source_policy_table = "silver.policy"
source_quotation_table = "silver.quotation"

dim_date_table = "gold.dimdate"
dim_customer_table = "gold.dimcustomer"
dim_agent_table = "gold.dimagent"
dim_provider_table = "gold.dimprovider"
dim_policy_info_table = "gold.dimpolicyinfo"

effective_date = ""
etl_date = ""

audit_session_id = ""
audit_table_session_id = ""
load_type = ""
target_schema = "gold"
audit_sink = "warehouse"
audit_warehouse_name = "audit_log"
audit_warehouse_workspace_id = ""
audit_warehouse_id = ""
useRootDefaultLakehouse = True

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from delta.tables import DeltaTable
from pyspark.sql import functions as F
from pyspark.sql import SparkSession
from datetime import datetime, timezone
from pyspark.sql.window import Window
import json
import builtins

if etl_date is None or str(etl_date).strip() == "" or str(etl_date).strip().startswith("@"):
    etl_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
if effective_date is None or str(effective_date).strip() == "":
    effective_date = etl_date

spark = SparkSession.builder.getOrCreate()

TARGET_TABLE = f"{target_schema}.{target_table}"

TARGET_COLUMNS = [
        "cancellation_id",
        "cancellation_date_key",
        "customer_key",
        "agent_key",
        "provider_key",
        "policy_info_key",
        "cancellation_reason",
        "refund_amount"
    ]
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

def filter_active_records( df):
    output_df = df
    if "_is_current" in output_df.columns:
        output_df = output_df.filter(F.col("_is_current") == True)
    if "_is_deleted" in output_df.columns:
        output_df = output_df.filter(F.col("_is_deleted") == False)
    if "is_current" in output_df.columns:
        output_df = output_df.filter(F.col("is_current") == True)
    if "is_deleted" in output_df.columns:
        output_df = output_df.filter(F.col("is_deleted") == False)
    return output_df

def filter_scd_lookup( df):
    if not effective_date or str(effective_date).strip() == "":
        return filter_active_records(df)

    output_df = df
    if "_is_deleted" in output_df.columns:
        output_df = output_df.filter(F.col("_is_deleted") == False)
    if "is_deleted" in output_df.columns:
        output_df = output_df.filter(F.col("is_deleted") == False)
    effective_dt = F.coalesce(
        F.to_date(F.lit(effective_date), "yyyy-MM-dd"),
        F.to_date(F.lit(effective_date))
    )
    if {"effective_start_date", "effective_end_date"}.issubset(set(output_df.columns)):
        output_df = output_df.filter(
            (F.col("effective_start_date").cast("date") <= effective_dt)
            & (F.col("effective_end_date").cast("date") > effective_dt)
        )
    elif "is_current" in output_df.columns:
        output_df = output_df.filter(F.col("is_current") == True)
    return output_df

def transform():
    cancellation_df = filter_active_records(
        spark.read.table(source_cancellation_table)
    )
    # self.source_row_count = cancellation_df.count()
    policy_df = filter_active_records(spark.read.table(source_policy_table))
    quotation_df = filter_active_records(
        spark.read.table(source_quotation_table)
    )

    dim_date_df = spark.read.table(dim_date_table)
    dim_customer_df = filter_scd_lookup(
        spark.read.table(dim_customer_table)
    )
    dim_agent_df = filter_scd_lookup(spark.read.table(dim_agent_table))
    dim_provider_df = filter_active_records(
        spark.read.table(dim_provider_table)
    )
    dim_policy_info_df = filter_active_records(
        spark.read.table(dim_policy_info_table)
    )

    dedupe_window = Window.partitionBy("cancellation_id").orderBy(
        F.col("last_updated").desc_nulls_last(),
        F.col("cancellation_date").desc_nulls_last(),
    )

    cancellation_df = (
        cancellation_df.filter(
            F.col("cancellation_id").isNotNull()
            & (F.length(F.trim(F.col("cancellation_id"))) > 0)
        )
        .withColumn("row_number", F.row_number().over(dedupe_window))
        .filter(F.col("row_number") == 1)
        .drop("row_number")
    )

    fact_df = (
        cancellation_df.alias("c")
        .join(policy_df.alias("p"), F.col("c.policy_id") == F.col("p.policy_id"), "left")
        .join(
            quotation_df.alias("q"),
            F.col("p.quotation_id") == F.col("q.quotation_id"),
            "left"
        )
        .join(
            dim_date_df.alias("dd"),
            F.to_date(F.col("c.cancellation_date")) == F.col("dd.full_date"),
            "left"
        )
        .join(
            dim_policy_info_df.alias("dpi"),
            F.col("c.policy_id") == F.col("dpi.policy_id"),
            "left"
        )
        .join(
            dim_customer_df.alias("dc"),
            F.col("p.customer_id") == F.col("dc.customer_id"),
            "left"
        )
        .join(
            dim_agent_df.alias("da"),
            F.col("q.agent_id") == F.col("da.agent_id"),
            "left"
        )
        .join(
            dim_provider_df.alias("dp"),
            F.col("p.provider_code") == F.col("dp.provider_code"),
            "left"
        )
        .select(
            F.trim(F.col("c.cancellation_id")).alias("cancellation_id"),
            F.coalesce(F.col("dd.date_key").cast("int"), F.lit(-1)).alias(
                "cancellation_date_key"
            ),
            F.coalesce(
                F.col("dc.customer_key").cast("bigint"),
                F.lit(-1).cast("bigint")
            ).alias("customer_key"),
            F.coalesce(
                F.col("da.agent_key").cast("bigint"),
                F.lit(-1).cast("bigint")
            ).alias("agent_key"),
            F.coalesce(
                F.col("dp.provider_key").cast("bigint"),
                F.lit(-1).cast("bigint")
            ).alias("provider_key"),
            F.coalesce(
                F.col("dpi.policy_info_key").cast("bigint"),
                F.lit(-1).cast("bigint")
            ).alias("policy_info_key"),
            F.coalesce(
                F.trim(F.col("c.cancellation_reason")),
                F.lit("Unknown Reason")
            ).alias("cancellation_reason"),
            F.col("c.refund_amount").cast("decimal(18,2)").alias("refund_amount")
        )
        .dropDuplicates(["cancellation_id"])
    )

    df = fact_df.select(TARGET_COLUMNS)

    return df

def write_to_gold( df):
    if not spark.catalog.tableExists(TARGET_TABLE):
        processed_rows = df.count()
        (
            df.write.format("delta")
            .mode("overwrite")
            .option("overwriteSchema", "true")
            .saveAsTable(TARGET_TABLE)
        )


    processed_rows = df.count()
    if processed_rows > 0:
        df.write.format("delta").mode("append").saveAsTable(
            TARGET_TABLE
        )
    return processed_rows

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
