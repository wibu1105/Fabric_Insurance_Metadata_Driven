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
target_table = "quotation"
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

TARGET_COLUMNS = ["quotation_id", "customer_id", "agent_id", "provider_code", "quotation_date", "quotation_status", "package_code", "premium_amount", "quotation_expiry_date"]

TARGET_TABLE = "quotation"


class SilverQuotation(SilverChildEngine):
    def transform(self):
        bronze_df = self.spark.read.table("bronze.quotation")
        customer_df = self.spark.read.table("silver.customers").select("customer_id").distinct()
        agent_df = self.spark.read.table("silver.agents").select("agent_id").distinct()
        provider_df = self.spark.read.table("silver.insurance_providers").select("provider_code").distinct()

        valid_df = (
            bronze_df
            .withColumn("quotation_id", F.trim(F.col("quotation_id")))
            .withColumn("customer_id", F.trim(F.col("customer_id")))
            .withColumn("agent_id", F.trim(F.col("agent_id")))
            .withColumn("provider_code", F.trim(F.col("provider_code")))
            .withColumn("quotation_status", F.trim(F.col("quotation_status")))
            .withColumn("package_code", F.trim(F.col("package_code")))
            .withColumn(
                "quotation_status",
                F.when(F.lower(F.col("quotation_status")).isin("converted", "c"), "CONVERTED")
                .when(F.lower(F.col("quotation_status")).isin("accepted", "a"), "ACCEPTED")
                .when(F.lower(F.col("quotation_status")).isin("rejected", "r"), "REJECTED")
                .when(F.lower(F.col("quotation_status")).isin("expired", "e"), "EXPIRED")
                .when(F.lower(F.col("quotation_status")).isin("quoted", "q"), "QUOTED")
                .otherwise("UNKNOWN"),
            )
            .withColumn(
                "package_code",
                F.when(F.lower(F.col("package_code")).isin("basic", "b"), "BASIC")
                .when(F.lower(F.col("package_code")).isin("standard", "s"), "STANDARD")
                .when(F.lower(F.col("package_code")).isin("premium", "p"), "PREMIUM")
                .when(F.lower(F.col("package_code")).isin("vip", "v.i.p", "v.i.p.", "v"), "VIP")
                .otherwise("UNKNOWN"),
            )
        )

        validations = [
            ((F.col("quotation_id").isNotNull()) & (F.length(F.col("quotation_id")) > 0), "quotation_id", "Quotation ID is null or empty"),
            ((F.col("customer_id").isNotNull()) & (F.length(F.col("customer_id")) > 0), "customer_id", "Customer ID is null or empty"),
            ((F.col("agent_id").isNotNull()) & (F.length(F.col("agent_id")) > 0), "agent_id", "Agent ID is null or empty"),
            ((F.col("provider_code").isNotNull()) & (F.length(F.col("provider_code")) > 0), "provider_code", "Provider code is null or empty"),
            (F.col("package_code").isin("BASIC", "STANDARD", "PREMIUM", "VIP"), "package_code", "Invalid package code"),
            (F.col("quotation_status").isin("CONVERTED", "ACCEPTED", "QUOTED", "REJECTED", "EXPIRED"), "quotation_status", "Invalid quotation status"),
            (F.col("quotation_date") <= F.current_timestamp(), "quotation_date", "Quotation date exceeds current date"),
            (F.col("premium_amount") >= 0, "premium_amount", "Premium amount must be more than or equal to 0"),
            (F.col("quotation_expiry_date") >= F.col("quotation_date"), "quotation_expiry_date", "Quotation expiry date must be later than quotation date"),
        ]
        for condition, column_name, reason in validations:
            valid_df = self.apply_validation(valid_df, "quotation", condition, column_name, reason)

        invalid_customer_df = valid_df.alias("q").join(customer_df.alias("c"), on="customer_id", how="left_anti")
        self.log_invalid_records(invalid_customer_df, "quotation", "customer_id", "Customer does not exist")
        valid_df = valid_df.alias("q").join(customer_df.alias("c"), on="customer_id", how="inner")

        invalid_agent_df = valid_df.alias("q").join(agent_df.alias("a"), on="agent_id", how="left_anti")
        self.log_invalid_records(invalid_agent_df, "quotation", "agent_id", "Agent does not exist")
        valid_df = valid_df.alias("q").join(agent_df.alias("a"), on="agent_id", how="inner")

        invalid_provider_df = valid_df.alias("q").join(provider_df.alias("p"), on="provider_code", how="left_anti")
        self.log_invalid_records(invalid_provider_df, "quotation", "provider_code", "Insurance provider does not exist")
        valid_df = valid_df.alias("q").join(provider_df.alias("p"), on="provider_code", how="inner")

        window_spec = Window.partitionBy("quotation_id").orderBy(F.col("quotation_date").desc())
        return valid_df.withColumn("row_num", F.row_number().over(window_spec)).filter(F.col("row_num") == 1).drop("row_num")


SilverQuotation(
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
