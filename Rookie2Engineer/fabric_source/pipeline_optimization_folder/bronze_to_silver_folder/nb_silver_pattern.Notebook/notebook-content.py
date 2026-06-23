# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "jupyter",
# META     "jupyter_kernel_name": "python3.12"
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

import json
import uuid
from datetime import datetime

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window

try:
    import com.microsoft.spark.fabric  # type: ignore # noqa: F401
    from com.microsoft.spark.fabric.Constants import Constants  # type: ignore
except Exception:
    Constants = None

spark = SparkSession.builder.getOrCreate()

def blank(value):
    return value is None or str(value).strip() == ""


def to_int(value, default=0):
    try:
        if blank(value):
            return default
        return int(float(str(value)))
    except Exception:
        return default


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

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

class SilverChildEngine:
    def __init__(self, target_schema, target_table, table_id, audit_session_id, audit_table_session_id, target_columns):
        self.spark = SparkSession.builder.getOrCreate()
        self.target_schema = target_schema
        self.target_table = str(target_table).strip().lower()
        self.table_id = to_int(table_id)
        self.audit_session_id = audit_session_id
        self.audit_table_session_id = audit_table_session_id or str(uuid.uuid4())
        self.target_columns = target_columns
        self.row_count = 0

    def transform(self):
        raise NotImplementedError("Child notebook must implement transform().")

    def use_warehouse_audit(self):
        return str(audit_sink).strip().lower() == "warehouse"

    def warehouse_table(self, table_name):
        if blank(audit_warehouse_name):
            raise ValueError("audit_warehouse_name is required when audit_sink = 'warehouse'")
        return f"{audit_warehouse_name}.audit.{table_name}"

    def write_warehouse_table(self, df, table_name, mode="append"):
        writer = df.write.mode(mode)
        if Constants is not None:
            if not blank(audit_warehouse_workspace_id):
                writer = writer.option(Constants.WorkspaceId, audit_warehouse_workspace_id)
            if not blank(audit_warehouse_id):
                writer = writer.option(Constants.DatawarehouseId, audit_warehouse_id)
        writer.synapsesql(self.warehouse_table(table_name))

    def log_invalid_records(self, invalid_df, table_name, invalid_column, invalid_reason):
        invalid_count = invalid_df.count()
        if invalid_count == 0:
            return

        audit_df = (
            invalid_df
            .withColumn("invalid_record_id", F.expr("uuid()"))
            .withColumn("audit_table_session_id", F.lit(self.audit_table_session_id))
            .withColumn("layer_name", F.lit("Silver"))
            .withColumn("table_name", F.lit(table_name))
            .withColumn("invalid_column", F.lit(invalid_column))
            .withColumn("invalid_reason", F.lit(invalid_reason))
            .withColumn("invalid_record_count", F.lit(invalid_count))
            .withColumn("record_payload", F.to_json(F.struct(*invalid_df.columns)))
            .withColumn("rejected_timestamp", F.current_timestamp())
            .select(
                "invalid_record_id",
                "audit_table_session_id",
                "layer_name",
                "table_name",
                "invalid_column",
                "invalid_reason",
                "invalid_record_count",
                "record_payload",
                "rejected_timestamp",
            )
        )
        if self.use_warehouse_audit():
            self.write_warehouse_table(audit_df, "audit_invalid_record")
        else:
            audit_df.write.format("delta").mode("append").saveAsTable("audit.audit_invalid_record")

    def apply_validation(self, df, table_name, condition, invalid_column, invalid_reason):
        valid_condition = F.coalesce(condition, F.lit(False))
        invalid_df = df.filter(~valid_condition)
        self.log_invalid_records(invalid_df, table_name, invalid_column, invalid_reason)
        return df.filter(valid_condition)

    def align_to_target_columns(self, df):
        missing_columns = [col_name for col_name in self.target_columns if col_name not in df.columns]
        if missing_columns:
            raise ValueError(f"{self.target_schema}.{self.target_table} missing columns: {missing_columns}")

        return df.select([F.col(col_name) for col_name in self.target_columns])

    def write_to_silver(self, output_df):
        self.spark.sql(f"CREATE SCHEMA IF NOT EXISTS {self.target_schema}")
        (
            output_df.write
            .format("delta")
            .mode("overwrite")
            .option("overwriteSchema", "true")
            .saveAsTable(f"{self.target_schema}.{self.target_table}")
        )

    def execute_pipeline(self):
        if self.target_table != TARGET_TABLE:
            raise ValueError(f"This notebook handles {TARGET_TABLE}, but target_table={self.target_table} was passed.")

        start_time = utc_now()
        df_out = self.transform()
        if df_out is None:
            raise ValueError(f"Transform returned None for {TARGET_TABLE}")

        output_df = self.align_to_target_columns(df_out)
        self.row_count = output_df.count()
        self.write_to_silver(output_df)
        end_time = utc_now()

        exit_notebook(json.dumps({
            "status": "success",
            "table_id": self.table_id,
            "target_table": TARGET_TABLE,
            "target_schema": self.target_schema,
            "audit_table_session_id": self.audit_table_session_id,
            "processed_rows": self.row_count,
            "start_time": iso_utc(start_time),
            "end_time": iso_utc(end_time),
        }, default=str))


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }
