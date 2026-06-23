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
target_table = "policy"
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

TARGET_COLUMNS = [
    "policy_id", 
    "quotation_id", 
    "customer_id", 
    "provider_code", 
    "policy_number", 
    "policy_start_date", 
    "policy_end_date", 
    "policy_status", 
    "premium_amount", 
    "issued_date", 
    "last_updated"
    ]

TARGET_TABLE = "policy"


class SilverPolicy(SilverChildEngine):
    def transform(self):
        df_bronze = self.spark.read.table("bronze.policy")
        window_spec = Window.partitionBy("policy_id").orderBy(F.col("last_updated").desc())
        valid_df = (
            df_bronze.withColumn("rn", F.row_number().over(window_spec))
            .filter(F.col("rn") == 1)
            .drop("rn")
            .withColumn("policy_start_date", F.to_date("policy_start_date"))
            .withColumn("policy_end_date", F.to_date("policy_end_date"))
            .withColumn("premium_amount", F.col("premium_amount").cast("decimal(18,2)"))
            .withColumn("issued_date", F.to_timestamp("issued_date"))
            .withColumn("last_updated", F.to_timestamp("last_updated"))
            .withColumn("policy_status", F.upper(F.trim(F.col("policy_status"))))
        )
        if "operation_type" in valid_df.columns:
            valid_df = valid_df.filter(F.upper(F.trim(F.col("operation_type"))) != "D")

        validations = [
            ((F.col("policy_end_date") > F.col("policy_start_date")) | F.col("policy_end_date").isNull(), "policy_end_date", "End date must be after start date"),
            (F.col("premium_amount") >= 0, "premium_amount", "Negative premium amount"),
            ((F.to_date(F.col("issued_date")) <= F.col("policy_start_date")) | F.col("issued_date").isNull(), "issued_date", "Issued date must be before or equal to start date"),
            (F.col("policy_status").isin(["EXPIRED", "CANCELLED", "ISSUED", "ACTIVE"]), "policy_status", "Invalid status value"),
        ]
        for condition, column_name, reason in validations:
            valid_df = self.apply_validation(valid_df, "policy", condition, column_name, reason)

        return valid_df


SilverPolicy(
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
