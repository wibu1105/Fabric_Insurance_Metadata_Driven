CREATE TABLE [cfg].[cfg_silver_gold_table] (

	[table_id] int NULL, 
	[layer_name] varchar(50) NULL, 
	[target_schema] varchar(100) NULL, 
	[target_table] varchar(255) NULL, 
	[primary_key_column] varchar(500) NULL, 
	[watermark_column] varchar(255) NULL, 
	[notebook_name] varchar(100) NULL, 
	[load_type] varchar(50) NULL, 
	[dependency_level] int NULL, 
	[is_active] bit NULL, 
	[created_date] datetime2(0) NULL, 
	[updated_date] datetime2(0) NULL
);