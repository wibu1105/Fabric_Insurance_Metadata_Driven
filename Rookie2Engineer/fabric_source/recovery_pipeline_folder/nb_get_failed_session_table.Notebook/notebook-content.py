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

p_audit_batch_id = ""
layer_name = ""

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Find the failed session table
import json

query = f"""
SELECT
    atsl.audit_session_id,
    atsl.audit_table_session_id,
    csgt.notebook_id,
    csgt.target_schema,
    csgt.target_table,
    csgt.table_id,
    csgt.dependency_level
FROM audit.audit_table_session_log atsl
JOIN audit.audit_session_log asl
    ON atsl.audit_session_id = asl.audit_session_id
JOIN audit.audit_batch_log abl
    ON abl.audit_batch_id = asl.audit_batch_id
JOIN cfg.cfg_silver_gold_table csgt
    ON csgt.table_id = atsl.table_id
WHERE abl.audit_batch_id = '{esc(p_audit_batch_id)}'
  AND lower(atsl.status) <> 'success'
  AND atsl.layer_name = '{esc(layer_name)}'
"""

df = spark.sql(query)

result = [
    {
        "audit_session_id": row["audit_session_id"],
        "audit_table_session_id": row["audit_table_session_id"],
        "notebook_id": row["notebook_id"],
        "target_schema": row["target_schema"],
        "target_table": row["target_table"],
        "table_id": row["table_id"],
        "dependency_level": row["dependency_level"]
    }
    for row in df.collect()
]

mssparkutils.notebook.exit(json.dumps(result))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
