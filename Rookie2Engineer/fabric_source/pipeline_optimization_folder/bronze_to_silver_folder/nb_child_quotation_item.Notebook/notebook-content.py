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
target_table = "quotation_item"
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

TARGET_COLUMNS = ["quotation_item_id", "quotation_id", "coverage_type", "coverage_amount", "deductible_amount"]

TARGET_TABLE = "quotation_item"


class SilverQuotationItem(SilverChildEngine):
    def transform(self):
        bronze_df = self.spark.read.table("bronze.quotation_item")
        quotation_df = self.spark.read.table("silver.quotation").select("quotation_id").distinct()

        valid_df = (
            bronze_df
            .withColumn("quotation_item_id", F.trim(F.col("quotation_item_id")))
            .withColumn("quotation_id", F.trim(F.col("quotation_id")))
            .withColumn("coverage_type", F.trim(F.col("coverage_type")))
        )

        validations = [
            ((F.col("quotation_item_id").isNotNull()) & (F.length(F.col("quotation_item_id")) > 0), "quotation_item_id", "Quotation Item ID is null or empty"),
            ((F.col("quotation_id").isNotNull()) & (F.length(F.col("quotation_id")) > 0), "quotation_id", "Quotation ID is null or empty"),
            (F.length(F.col("coverage_type")) <= 100, "coverage_type", "Coverage type exceeds 100 characters"),
            (F.col("coverage_amount") >= 0, "coverage_amount", "Coverage amount must be more than or equal to 0"),
            (F.col("deductible_amount") >= 0, "deductible_amount", "Deductible amount must be more than or equal to 0"),
        ]
        for condition, column_name, reason in validations:
            valid_df = self.apply_validation(valid_df, "quotation_item", condition, column_name, reason)

        invalid_quotation_df = valid_df.alias("v").join(quotation_df.alias("q"), on="quotation_id", how="left_anti")
        self.log_invalid_records(invalid_quotation_df, "quotation_item", "quotation_id", "Quotation does not exist")
        valid_df = valid_df.alias("v").join(quotation_df.alias("q"), on="quotation_id", how="inner")
        return valid_df.dropDuplicates(["quotation_item_id"])


SilverQuotationItem(
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
