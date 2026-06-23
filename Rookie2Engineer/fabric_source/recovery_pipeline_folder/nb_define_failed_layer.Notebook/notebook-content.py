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

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

query = f"""
SELECT DISTINCT atsl.layer_name
FROM audit.audit_table_session_log atsl
JOIN audit.audit_session_log asl
    ON atsl.audit_session_id = asl.audit_session_id
JOIN audit.audit_batch_log abl
    ON abl.audit_batch_id = asl.audit_batch_id
WHERE abl.audit_batch_id = '{esc(p_audit_batch_id)}'
  AND lower(atsl.status) <> 'success'
"""

df = spark.sql(query)

layer = df.first()["layer_name"]

mssparkutils.notebook.exit(layer)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
