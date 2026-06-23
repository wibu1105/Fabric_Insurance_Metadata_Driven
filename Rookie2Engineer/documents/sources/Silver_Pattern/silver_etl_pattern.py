from pyspark.sql import SparkSession 
from pyspark.sql.functions import * 
from pyspark.sql.types import * 



class LayerEngine:
    def __init__(self, target_schema, target_table, table_id, audit_table_session_id): # them audit_table_section_id
        self.spark = SparkSession.builder.getOrCreate()
        self.p_target_schema = target_schema
        self.destination_table = target_table
        self.p_audit_table_session_id = audit_table_session_id
        self.p_table_id = table_id
        self.p_target_table = f"{target_schema}.{target_table}"
        self.row_count = 0

    def transform(self):
        raise NotImplementedError("The transform method must be explicitly defined")

    def write_to_silver(self, df):
        df.write.format("delta").mode("overwrite").saveAsTable(self.p_target_table)

    def execute_pipeline(self):
        """Master orchestrator managing the full operational lifecycle of the transition."""
        try:
            #read
            df_out = self.transform()

            #row count
            self.row_count = df_out.count()
            print(f"Total processed rows: {self.row_count}")

            #write
            self.write_to_silver(df_out)

            #sucess
            end_time = str(current_timest)
            print(f"-----> {self.destination_table.upper()} SUCCESS")
            mssparkutils.notebook.exit(
                f"SUCCESS|{self.p_table_id}|{self.row_count}|{end_time}")

        # catch error
        except Exception as e:
            end_time = str(current_timest)
            error_msg = str(e).replace("|", " ").replace("\n", " ")
            print(f"{self.destination_table.upper()} FAILED")
            print(error_msg)
            mssparkutils.notebook.exit(
                f"FAILED|{self.p_table_id}|{error_msg}|{end_time}")

