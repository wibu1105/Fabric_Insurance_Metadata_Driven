CREATE TABLE [validate].[dq_pk_duplicate_summary] (

	[check_type] varchar(50) NOT NULL, 
	[status] varchar(20) NOT NULL, 
	[table_name] varchar(128) NOT NULL, 
	[key_column] varchar(128) NOT NULL, 
	[duplicate_key_count] bigint NOT NULL, 
	[extra_duplicate_rows] bigint NOT NULL
);