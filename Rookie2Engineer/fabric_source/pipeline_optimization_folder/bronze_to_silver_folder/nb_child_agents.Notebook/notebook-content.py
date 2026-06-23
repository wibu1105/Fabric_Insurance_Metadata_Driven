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

audit_session_id = ""
audit_table_session_id = ""
table_id = ""
load_type = ""
target_schema = "silver"
target_table = "agents"
audit_sink = "warehouse"
audit_warehouse_name = "Rookie2Engineer_Warehouse"
audit_warehouse_workspace_id = ""
audit_warehouse_id = ""
useRootDefaultLakehouse = True

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

%run nb_silver_pattern

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

TARGET_COLUMNS = ["agent_id", "agent_name", "region", "branch", "manager_name", "created_date"]

TARGET_TABLE = "agents"


class SilverAgents(SilverChildEngine):
    def transform(self):
        bronze_df = self.spark.read.table("bronze.agents")
        valid_df = (
            bronze_df
            .withColumn("agent_id", F.trim(F.col("agent_id")))
            .withColumn("agent_name", F.trim(F.col("agent_name")))
            .withColumn("region", F.trim(F.col("region")))
            .withColumn("branch", F.trim(F.col("branch")))
            .withColumn("manager_name", F.trim(F.col("manager_name")))
        )

        validations = [
            ((F.col("agent_id").isNotNull()) & (F.length(F.col("agent_id")) > 0), "agent_id", "Agent ID is null or empty"),
            ((F.length(F.col("agent_name")) <= 200) & (F.col("agent_name").isNotNull()), "agent_name", "Agent name exceeds 200 characters"),
            (F.length(F.col("region")) <= 100, "region", "Region exceeds 100 characters"),
            (F.length(F.col("branch")) <= 100, "branch", "Branch exceeds 100 characters"),
            (F.length(F.col("manager_name")) <= 200, "manager_name", "Manager name exceeds 200 characters"),
        ]
        for condition, column_name, reason in validations:
            valid_df = self.apply_validation(valid_df, "agents", condition, column_name, reason)

        window_spec = Window.partitionBy("agent_id").orderBy(F.col("created_date").desc())
        return valid_df.withColumn("row_num", F.row_number().over(window_spec)).filter(F.col("row_num") == 1).drop("row_num")


SilverAgents(
    target_schema=target_schema,
    target_table=target_table,
    table_id=table_id,
    audit_session_id=audit_session_id,
    audit_table_session_id=audit_table_session_id,
    target_columns=TARGET_COLUMNS,
).execute_pipeline()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
