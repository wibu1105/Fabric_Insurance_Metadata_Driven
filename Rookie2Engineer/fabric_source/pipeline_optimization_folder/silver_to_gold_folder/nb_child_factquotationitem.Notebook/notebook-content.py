# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# PARAMETERS CELL ********************

target_schema          = "gold"
target_table           = "factquotationitem"
table_id               = 4014
audit_table_session_id = "manual_run"
etl_date = ""
audit_session_id = ""
load_type = ""
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

spark = SparkSession.builder.getOrCreate()

TARGET_TABLE = f"{target_schema}.{target_table}"
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
    quotation_item = spark.read.table("silver.quotation_item").alias("qi")
    # self.source_row_count = quotation_item.count()
    quotation = spark.read.table("silver.quotation").alias("q")

    dim_date = spark.read.table("gold.DimDate").alias("dd")
    dim_provider = spark.read.table("gold.DimProvider").alias("dp")
    dim_customer = spark.read.table("gold.DimCustomer").alias("dcm")
    dim_agent = spark.read.table("gold.DimAgent").alias("da")
    dim_quote = spark.read.table("gold.DimQuotationInfo").alias("dqi")

    run_date = datetime.strptime(etl_date, "%Y-%m-%d").date()

    dim_customer = dim_customer.filter(
        (F.col("dcm.effective_start_date").cast("date") <= run_date) &
        (F.col("dcm.effective_end_date").cast("date") > run_date)
    )
    dim_agent = dim_agent.filter(
        (F.col("da.effective_start_date").cast("date") <= run_date) &
        (F.col("da.effective_end_date").cast("date") > run_date)
    )

    df = (
        quotation_item
        .join(quotation, F.col("qi.quotation_id") == F.col("q.quotation_id"), "left")
        .join(dim_date, F.col("q.quotation_date").cast("date") == F.col("dd.full_date"), "left")
        .join(dim_provider, F.col("q.provider_code") == F.col("dp.provider_code"), "left")
        .join(dim_customer, F.col("q.customer_id") == F.col("dcm.customer_id"), "left")
        .join(dim_agent, F.col("q.agent_id") == F.col("da.agent_id"), "left")
        .join(dim_quote, F.col("q.quotation_id") == F.col("dqi.quotation_id"), "left")
    )

    item_count_window = Window.partitionBy(F.col("qi.quotation_id"))
    quotation_premium_amount = (
        F.col("q.premium_amount") /
        F.count(F.col("qi.quotation_item_id")).over(item_count_window)
    ).cast("decimal(18,2)")

    df = df.select(
        F.col("dcm.customer_key").alias("customer_key"),
        F.col("da.agent_key").alias("agent_key"),
        F.col("dp.provider_key").alias("provider_key"),
        F.col("qi.coverage_type").alias("coverage_type"),
        F.col("dqi.quotation_info_key").alias("quotation_info_key"),
        F.col("dd.date_key").cast("int").alias("quotation_date_key"),
        F.col("q.quotation_expiry_date").alias("quotation_expiry_date"),
        F.col("q.quotation_status").alias("quotation_status"),
        quotation_premium_amount.alias("quotation_premium_amount"),
        F.col("qi.quotation_item_id").alias("quotation_item_id"),
        F.col("qi.coverage_amount").cast("decimal(18,2)").alias("coverage_amount"),
        F.col("qi.deductible_amount").cast("decimal(18,2)").alias("deductible_amount")
    )
    
    return df

# The code above is untouched, only from this part below is changed
def write_to_gold( df):
    if not spark.catalog.tableExists(TARGET_TABLE):
        processed_rows = df.count()
        (
            df.write.format("delta")
            .mode("overwrite")
            .option("overwriteSchema", "true")
            .saveAsTable(TARGET_TABLE)
        )

    # Fact Quotation Item don't have any PK (like Fact Policy), so I use composite key to check
    # May check on these columns to create a better composite key
    business_columns = ["customer_key", "agent_key", "provider_key", "quotation_info_key", "quotation_date_key"]

    processed_rows = df.count()

    if processed_rows > 0:
        (
            df.write.format("delta")
            .mode("append")
            .saveAsTable(TARGET_TABLE)
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
