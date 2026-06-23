
""" REMEMBER: 
		self.spark = SparkSession.builder.getOrCreate()
	    self.p_target_schema = target_schema
	    self.destination_table = target_table
	    self.p_audit_table_session_id = audit_table_session_id
	    self.p_table_id = table_id
	    self.p_target_table = f"{target_schema}.{target_table}"
	    self.row_count = 0
"""



target_schema = "default"  		# default   
target_table  = "default"		# default   
table_id      = 0               # default   
audit_table_session_id = 0      # default   

%run nb_layer_engine

class Gold_PolicyFact(LayerEngine):
    def transform(self):
        policy   = self.spark.read.table("lakehouse.silver_policy")
        customer = self.spark.read.table("lakehouse.silver_customer")
        agent    = self.spark.read.table("lakehouse.silver_agent")

        df_policy_clean = policy.filter(
        	#filter 
        	)

        df = (
            df_policy_clean
            .join(customer, "customer_id", "inner")
            .join(agent, "agent_id", "inner")
        	)
        return df

Gold_PolicyFact(target_schema, target_table, table_id, audit_table_session_id).execute_pipeline()

