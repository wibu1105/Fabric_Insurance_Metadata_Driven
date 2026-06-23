CREATE TABLE [validate].[dq_pk_null_summary] (

	[check_type] varchar(50) NOT NULL, 
	[status] varchar(20) NOT NULL, 
	[table_name] varchar(128) NOT NULL, 
	[key_column] varchar(128) NOT NULL, 
	[null_key_count] bigint NOT NULL, 
	[expected_result] varchar(500) NULL
);