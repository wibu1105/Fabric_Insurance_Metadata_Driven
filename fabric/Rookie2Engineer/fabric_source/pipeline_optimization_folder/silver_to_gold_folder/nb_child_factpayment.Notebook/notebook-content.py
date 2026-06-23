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

target_schema          = "gold"
target_table           = "factpayment"
table_id               = 4016
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
    policy = spark.read.table("silver.policy").alias("py")
    quotation = spark.read.table("silver.quotation").alias("q")
    payment = spark.read.table("silver.payment").alias("p")
    # self.source_row_count = payment.count()

    dim_customer = spark.read.table("gold.DimCustomer").alias("dcm")
    dim_agent = spark.read.table("gold.DimAgent").alias("da")
    dim_provider = spark.read.table("gold.DimProvider").alias("dp")
    dim_date = spark.read.table("gold.DimDate").alias("dd")
    dim_policy_info = spark.read.table("gold.DimPolicyInfo").alias("dpi")
    dim_payment_type = spark.read.table("gold.DimPaymentType").alias("dpt")

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
        payment
        .join(dim_date, F.col("p.payment_date").cast("date") == F.col("dd.full_date"), "left")
        .join(dim_policy_info, F.col("p.policy_id") == F.col("dpi.policy_id"), "left")
        .join(dim_payment_type, F.col("p.payment_method") == F.col("dpt.payment_method"), "left")
        .join(policy, F.col("p.policy_id") == F.col("py.policy_id"), "left")
        .join(quotation, F.col("py.quotation_id") == F.col("q.quotation_id"), "left")
        .join(dim_customer, F.col("py.customer_id") == F.col("dcm.customer_id"), "left")
        .join(dim_provider, F.col("py.provider_code") == F.col("dp.provider_code"), "left")
        .join(dim_agent, F.col("q.agent_id") == F.col("da.agent_id"), "left")
    )

    df = df.select(
        F.col("p.payment_id").alias("payment_id"),
        F.col("dcm.customer_key").alias("customer_key"),
        F.col("da.agent_key").alias("agent_key"),
        F.col("dp.provider_key").alias("provider_key"),
        F.col("dpi.policy_info_key").alias("policy_info_key"),
        F.col("dd.date_key").cast("int").alias("payment_date_key"),
        F.col("p.payment_status").alias("payment_status"),
        F.col("dpt.payment_type_key").alias("payment_type_key"),
        F.col("p.payment_amount").cast("decimal(18,2)").alias("payment_amount"),
        F.col("p.transaction_reference").alias("transaction_reference")
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
