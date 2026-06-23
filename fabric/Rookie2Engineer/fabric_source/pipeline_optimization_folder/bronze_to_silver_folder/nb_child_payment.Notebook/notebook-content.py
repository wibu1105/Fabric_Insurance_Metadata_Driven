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
target_table = "payment"
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

TARGET_COLUMNS = ["payment_id", "policy_id", "payment_date", "payment_method", "payment_status", "payment_amount", "transaction_reference", "last_updated"]

TARGET_TABLE = "payment"


class SilverPayment(SilverChildEngine):
    def transform(self):
        df_bronze = self.spark.read.table("bronze.payment")
        window_spec = Window.partitionBy("payment_id").orderBy(F.col("last_updated").desc())
        valid_df = (
            df_bronze.withColumn("rn", F.row_number().over(window_spec))
            .filter(F.col("rn") == 1)
            .drop("rn")
            .withColumn("payment_date", F.to_timestamp("payment_date"))
            .withColumn("payment_amount", F.col("payment_amount").cast("decimal(18,2)"))
            .withColumn("last_updated", F.to_timestamp("last_updated"))
            .withColumn("payment_status", F.upper(F.trim(F.col("payment_status"))))
            .withColumn("payment_method", F.trim(F.col("payment_method")))
            .withColumn("transaction_reference", F.trim(F.col("transaction_reference")))
        )
        if "operation_type" in valid_df.columns:
            valid_df = valid_df.filter(F.upper(F.trim(F.col("operation_type"))) != "D")

        validations = [
            ((F.col("payment_date") <= F.current_timestamp()) | F.col("payment_date").isNull(), "payment_date", "Payment date must be before or equal to current timestamp"),
            (F.col("payment_amount") >= 0, "payment_amount", "Negative payment amount"),
            (F.col("payment_status").isin(["PAID", "FAILED", "PENDING", "REFUNDED"]), "payment_status", "Invalid payment status value"),
            (F.upper(F.col("payment_method")).isin(["BANK TRANSFER", "CREDIT CARD", "E-WALLET"]), "payment_method", "Invalid payment method value"),
        ]
        for condition, column_name, reason in validations:
            valid_df = self.apply_validation(valid_df, "payment", condition, column_name, reason)

        return valid_df


SilverPayment(
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
