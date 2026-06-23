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
target_table = "vehicle"
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

TARGET_COLUMNS = ["vehicle_id", "customer_id", "plate_number", "vehicle_brand", "vehicle_model", "manufacture_year", "vehicle_value"]

TARGET_TABLE = "vehicle"


class SilverVehicle(SilverChildEngine):
    def transform(self):
        bronze_df = self.spark.read.table("bronze.vehicle")
        customer_df = self.spark.read.table("silver.customers").select("customer_id").distinct()

        valid_df = (
            bronze_df
            .withColumn("vehicle_id", F.trim(F.col("vehicle_id")))
            .withColumn("customer_id", F.trim(F.col("customer_id")))
            .withColumn("plate_number", F.trim(F.col("plate_number")))
            .withColumn("vehicle_brand", F.trim(F.col("vehicle_brand")))
            .withColumn("vehicle_model", F.trim(F.col("vehicle_model")))
        )

        validations = [
            ((F.col("vehicle_id").isNotNull()) & (F.length(F.col("vehicle_id")) > 0), "vehicle_id", "Vehicle ID is null or empty"),
            (F.length(F.col("plate_number")) <= 20, "plate_number", "Plate number exceeds 20 characters"),
            (F.length(F.col("vehicle_brand")) <= 100, "vehicle_brand", "Vehicle brand exceeds 100 characters"),
            (F.length(F.col("vehicle_model")) <= 100, "vehicle_model", "Vehicle model exceeds 100 characters"),
            (F.col("manufacture_year") <= F.year(F.current_date()), "manufacture_year", "Manufacture year exceeds current year"),
            (F.col("vehicle_value") >= 0, "vehicle_value", "Vehicle value must be more than or equal to 0"),
        ]
        for condition, column_name, reason in validations:
            valid_df = self.apply_validation(valid_df, "vehicle", condition, column_name, reason)

        invalid_customer_df = valid_df.alias("v").join(customer_df.alias("c"), on="customer_id", how="left_anti")
        self.log_invalid_records(invalid_customer_df, "vehicle", "customer_id", "Customer does not exist")
        valid_df = valid_df.alias("v").join(customer_df.alias("c"), on="customer_id", how="inner")

        window_spec = Window.partitionBy("customer_id").orderBy(F.col("vehicle_id"))
        valid_df = valid_df.withColumn("row_num", F.row_number().over(window_spec)).filter(F.col("row_num") == 1).drop("row_num")

        plate_window = Window.partitionBy("plate_number").orderBy(F.col("vehicle_id").desc())
        duplicate_plate_df = valid_df.withColumn("plate_rank", F.row_number().over(plate_window)).filter(F.col("plate_rank") > 1).drop("plate_rank")
        self.log_invalid_records(duplicate_plate_df, "vehicle", "plate_number", "Duplicate plate number detected")
        return valid_df.withColumn("plate_rank", F.row_number().over(plate_window)).filter(F.col("plate_rank") == 1).drop("plate_rank")


SilverVehicle(
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
