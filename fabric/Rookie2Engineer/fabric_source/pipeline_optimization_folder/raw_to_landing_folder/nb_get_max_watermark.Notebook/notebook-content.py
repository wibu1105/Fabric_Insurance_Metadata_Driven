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

# PARAMETERS CELL ********************

event_type = ""
destination_schema = ""
destination_table = ""
watermark_column = ""
watermark_value = ""

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

import json
import uuid
def esc(v):
    if v is None:
        return ""
    return str(v).replace("'", "''")

def blank(v):
    return v is None or str(v).strip() == ""

def ident(v):
    if blank(v):
        raise ValueError("Identifier value is required")
    return "`" + str(v).replace("`", "``") + "`"

def exit_notebook(value):
    out = "" if value is None else str(value)
    try:
        notebookutils.notebook.exit(out)
    except NameError:
        mssparkutils.notebook.exit(out)

def get_max_watermark():
    if blank(watermark_column):
        exit_notebook("")
    row = spark.sql(f"""
    SELECT CAST(MAX({ident(watermark_column)}) AS STRING) AS max_watermark_value
    FROM {ident(destination_schema)}.{ident(destination_table)}
    """).first()
    exit_notebook(row["max_watermark_value"] if row else "")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
