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

import json
import uuid
from datetime import datetime

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

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
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

class GoldChildEngine:
    def __init__(self, target_schema, target_table, table_id, audit_session_id, audit_table_session_id):
        self.spark = SparkSession.builder.getOrCreate()
        self.target_schema = target_schema
        self.target_table = str(target_table).strip().lower()
        self.full_table_name = f"{target_schema}.{self.target_table}"
        self.table_id = to_int(table_id)
        self.audit_session_id = audit_session_id
        self.audit_table_session_id = audit_table_session_id or str(uuid.uuid4())
        self.processed_rows = 0

    def extract(self):
        raise NotImplementedError("Gold child notebook must implement extract().")

    def transform(self, source_df):
        raise NotImplementedError("Gold child notebook must implement transform(source_df).")

    def load(self, output_df):
        raise NotImplementedError("Gold child notebook must implement load(output_df).")

    def execute_pipeline(self):
        start_time = utc_now()
        source_df = self.extract()
        output_df = self.transform(source_df)
        if output_df is None:
            raise ValueError(f"Transform returned None for {self.full_table_name}")

        self.processed_rows = to_int(self.load(output_df))
        end_time = utc_now()

        exit_notebook(json.dumps({
            "status": "success",
            "table_id": self.table_id,
            "target_table": self.target_table,
            "target_schema": self.target_schema,
            "audit_table_session_id": self.audit_table_session_id,
            "processed_rows": self.processed_rows,
            "start_time": iso_utc(start_time),
            "end_time": iso_utc(end_time),
        }, default=str))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
