

""" REMEMBER: 
        self.spark = SparkSession.builder.getOrCreate()
        self.p_target_schema = target_schema
        self.destination_table = target_table
        self.p_audit_table_session_id = audit_table_session_id
        self.p_table_id = table_id
        self.p_target_table = f"{target_schema}.{target_table}"
        self.row_count = 0
"""

target_schema = "default"       # default   
target_table  = "default"       # default   
table_id      = 0               # default   
audit_table_session_id = 0      # default   

%run nb_layer_engine


class Silver_Customer(LayerEngine):
    def transform(self):
        df = self.spark.read.table("lakehouse.raw_customer")
        
        df = (
            df
            .withColumn("customer_id", col("customer_id").cast("int"))
            .withColumn("email", lower(trim(col("email"))))
            .dropDuplicates(["customer_id"])
        )
        return df


Silver_Customer(target_schema, target_table, table_id, audit_table_session_id).execute_pipeline()