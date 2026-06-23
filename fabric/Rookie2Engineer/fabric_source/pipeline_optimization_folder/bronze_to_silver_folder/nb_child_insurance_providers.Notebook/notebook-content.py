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

audit_session_id = ""
audit_table_session_id = ""
table_id = ""
load_type = ""
target_schema = "silver"
target_table = "insurance_providers"
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

TARGET_COLUMNS = ["provider_code", "provider_name", "provider_group", "active_flag"]

TARGET_TABLE = "insurance_providers"


class SilverInsuranceProviders(SilverChildEngine):
    def transform(self):
        bronze_df = self.spark.read.table("bronze.insurance_providers")
        valid_df = (
            bronze_df
            .withColumn("provider_code", F.trim(F.col("provider_code")))
            .withColumn("provider_name", F.trim(F.col("provider_name")))
            .withColumn("provider_group", F.trim(F.col("provider_group")))
        )

        validations = [
            ((F.col("provider_code").isNotNull()) & (F.length(F.col("provider_code")) > 0), "provider_code", "Provider code is null or empty"),
            (F.length(F.col("provider_name")) <= 200, "provider_name", "Provider name exceeds 200 characters"),
            (F.length(F.col("provider_group")) <= 100, "provider_group", "Provider group exceeds 100 characters"),
            (F.col("active_flag").isin(0, 1), "active_flag", "Active flag must be 0 or 1"),
        ]
        for condition, column_name, reason in validations:
            valid_df = self.apply_validation(valid_df, "insurance_providers", condition, column_name, reason)

        return valid_df.dropDuplicates(["provider_code"])


SilverInsuranceProviders(
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
