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

log_target = ""
session_status = ""
table_status = ""
audit_session_id = ""
audit_table_session_id = ""
action = "update"


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# -----------------------------------------------------------------------------
# 1. Logging
# -----------------------------------------------------------------------------
if log_target == "session":
    if action == "update":
        spark.sql(f"""
            UPDATE audit.audit_session_log 
                SET session_status = '{session_status}', 
                    session_end = CASE 
                        WHEN '{session_status}' IN ('success', 'failed') THEN current_timestamp() 
                        ELSE NULL 
                    END
                WHERE audit_session_id = '{audit_session_id}'
        """)
elif log_target == "table":
    if action == "update":
        spark.sql(f"""
            UPDATE audit.audit_table_session_log
                SET status = '{table_status}', 
                    end_time = CASE 
                        WHEN '{table_status}' IN ('success', 'failed') THEN current_timestamp() 
                        ELSE NULL 
                    END,
                    updated_at = CASE 
                        WHEN '{table_status}' IN ('success', 'failed') THEN current_timestamp() 
                        ELSE NULL 
                    END
                WHERE audit_table_session_id = '{audit_table_session_id}'
        """)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
