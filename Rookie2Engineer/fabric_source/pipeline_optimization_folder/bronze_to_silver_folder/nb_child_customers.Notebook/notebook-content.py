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
target_table = "customers"
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

TARGET_COLUMNS = ["customer_id", "full_name", "gender", "dob", "phone_number", "email", "city", "district", "created_date"]

TARGET_TABLE = "customers"


class SilverCustomers(SilverChildEngine):
    def transform(self):
        bronze_df = self.spark.read.table("bronze.customers")
        clean_df = (
            bronze_df
            .withColumn("customer_id", F.trim(F.col("customer_id")))
            .withColumn("full_name", F.trim(F.col("full_name")))
            .withColumn("gender", F.trim(F.col("gender")))
            .withColumn("phone_number", F.trim(F.col("phone_number")))
            .withColumn("email", F.trim(F.col("email")))
            .withColumn("city", F.trim(F.col("city")))
            .withColumn("district", F.trim(F.col("district")))
            .withColumn(
                "gender",
                F.when(F.lower(F.col("gender")).isin("male", "m"), "Male")
                .when(F.lower(F.col("gender")).isin("female", "f"), "Female")
                .otherwise("Unknown"),
            )
        )

        valid_df = clean_df
        validations = [
            ((F.col("customer_id").isNotNull()) & (F.length(F.col("customer_id")) > 0), "customer_id", "Customer ID is null or empty"),
            (F.length(F.col("full_name")) <= 200, "full_name", "Full name exceeds 200 characters"),
            (F.col("gender").isin("Male", "Female"), "gender", "Invalid gender"),
            (F.col("dob") < F.current_date(), "dob", "DOB must be before current date"),
            (F.col("phone_number").rlike(r"^[0-9]{10}$"), "phone_number", "Invalid phone number format"),
            (F.col("email").rlike(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"), "email", "Invalid email format"),
            (F.length(F.col("city")) <= 100, "city", "City exceeds 100 characters"),
            (F.length(F.col("district")) <= 100, "district", "District exceeds 100 characters"),
        ]
        for condition, column_name, reason in validations:
            valid_df = self.apply_validation(valid_df, "customers", condition, column_name, reason)

        window_spec = Window.partitionBy("customer_id").orderBy(F.col("created_date").desc())
        return valid_df.withColumn("row_num", F.row_number().over(window_spec)).filter(F.col("row_num") == 1).drop("row_num")


SilverCustomers(
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
