CREATE TABLE [cfg].[cfg_table_watermark] (

	[table_id] int NULL, 
	[last_watermark_value] datetime2(0) NULL, 
	[last_audit_session] varchar(100) NULL, 
	[last_load_time] datetime2(0) NULL, 
	[created_date] datetime2(0) NULL, 
	[updated_date] datetime2(0) NULL
);