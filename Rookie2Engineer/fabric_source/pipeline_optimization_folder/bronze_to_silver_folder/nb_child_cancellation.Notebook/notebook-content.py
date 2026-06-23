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
target_table = "cancellation"
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

TARGET_COLUMNS = ["cancellation_id", "policy_id", "cancellation_date", "cancellation_reason", "refund_amount", "last_updated"]

TARGET_TABLE = "cancellation"


class SilverCancellation(SilverChildEngine):
    def transform(self):
        df_bronze = self.spark.read.table("bronze.cancellation")
        window_spec = Window.partitionBy("cancellation_id").orderBy(F.col("last_updated").desc())
        valid_df = (
            df_bronze.withColumn("rn", F.row_number().over(window_spec))
            .filter(F.col("rn") == 1)
            .drop("rn")
            .withColumn("cancellation_date", F.to_timestamp("cancellation_date"))
            .withColumn("refund_amount", F.col("refund_amount").cast("decimal(18,2)"))
            .withColumn("last_updated", F.to_timestamp("last_updated"))
            .withColumn("cancellation_reason", F.trim(F.col("cancellation_reason")))
        )
        if "operation_type" in valid_df.columns:
            valid_df = valid_df.filter(F.upper(F.trim(F.col("operation_type"))) != "D")

        validations = [
            ((F.col("cancellation_date") <= F.current_timestamp()) | F.col("cancellation_date").isNull(), "cancellation_date", "Cancellation date must be before or equal to current timestamp"),
            (F.col("refund_amount") >= 0, "refund_amount", "Negative refund amount"),
            ((F.col("cancellation_reason").isNotNull()) & (F.length(F.col("cancellation_reason")) > 0), "cancellation_reason", "Cancellation reason must not be blank"),
        ]
        for condition, column_name, reason in validations:
            valid_df = self.apply_validation(valid_df, "cancellation", condition, column_name, reason)

        return valid_df


SilverCancellation(
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
