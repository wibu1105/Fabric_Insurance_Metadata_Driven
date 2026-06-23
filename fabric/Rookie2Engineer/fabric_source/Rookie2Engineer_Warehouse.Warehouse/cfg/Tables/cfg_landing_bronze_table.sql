CREATE TABLE [cfg].[cfg_landing_bronze_table] (

	[table_id] int NULL, 
	[source_system] varchar(100) NULL, 
	[source_schema] varchar(100) NULL, 
	[source_table] varchar(255) NULL, 
	[source_watermark_column] varchar(255) NULL, 
	[destination_system] varchar(100) NULL, 
	[destination_schema] varchar(100) NULL, 
	[destination_table] varchar(255) NULL, 
	[primary_key_column] varchar(500) NULL, 
	[load_type] varchar(50) NULL, 
	[is_active] bit NULL, 
	[created_date] datetime2(0) NULL, 
	[updated_date] datetime2(0) NULL
);