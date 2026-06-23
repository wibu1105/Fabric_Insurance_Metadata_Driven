CREATE TABLE [validate].[dq_grain_summary] (

	[fact_table] varchar(128) NOT NULL, 
	[total_rows] bigint NOT NULL, 
	[distinct_grain_rows] bigint NOT NULL, 
	[duplicate_rows] bigint NOT NULL
);